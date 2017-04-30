import datetime
import json
import os
import shutil
from flask import render_template, redirect, request, g, url_for, flash, abort,\
                  send_from_directory, session
from flask_login import login_required
from flask_security import current_user
from werkzeug.utils import secure_filename

from .analysis import run_analysis, terminate_analysis
from .view_functions import save_study, get_form, save_analysis, \
                           get_studies_array, get_analyses_array, \
                           get_user_folder, security_check
from backend.utils.check_uploaded_files import clear_up_study
from . import app, db, models
from .forms import UploadForm, AnalysisForm

# -----------------------------------------------------------------------------
# INDEX & ABOUT & HELP & TC & DEMO PAGES
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/tc')
def tc():
    return render_template('tc.html')

# =============================================================================
#
#                                UPLOAD
#
# =============================================================================

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Handles the upload of files. Uses AJAX POST requests to do server side form
    validation, which looks like client site validation.
    """

    # -------------------------------------------------------------------------
    # we got a POST AJAX request from the client
    if request.method == 'POST':
        # rebuild form from request.values and request.files
        form = UploadForm(data=get_form(request.values, request.files))
        # we use the check flag to see if we get a POST request with an already
        # validated form whose files need to be saved, or an unvalidated one
        # that we have to validate using the validators defined in UploadForm
        try:
            check = request.form['check']
            if check == 'true':
                check = True
            else:
                check = False
        except:
            return json.dumps(dict(status='invalid'))

        # ---------------------------------------------------------------------
        # we got a form that needs to be validated
        if check:
            if form.validate_on_submit():
                # we passed validation, so let's return OK
                return json.dumps(dict(status='OK'))
            else:
                # failed validation, let's create JSON with errors
                return json.dumps(dict(status='errors', errors=form.errors))

        # ---------------------------------------------------------------------
        # we got a form, that has passed validation, let's save the files
        else:
            try:
                return save_study(form, request.files)
            except:
                # couldn't save the files for some reason, let's try again and
                # clear up folder to make sure no corrupted files left behind
                user_folder = get_user_folder()
                study_folder = secure_filename(form.study_name.data)
                user_data_folder = os.path.join(user_folder, study_folder)
                clear_up_study(user_data_folder)
                return json.dumps(dict(status='invalid'))

    # -------------------------------------------------------------------------
    # render the form for the first time via GET
    else:
        form = UploadForm()
        # check how many studies the current user has now and had in the past
        too_many_studies = 0
        if len(current_user.studies.all()) >= app.config['ACTIVE_STUDY_PER_USER']:
            too_many_studies = 1
        if current_user.num_studies >= app.config['STUDY_PER_USER']:
            too_many_studies = 2
        return render_template('upload.html', form=form,
                               too_many_studies=too_many_studies)

# -----------------------------------------------------------------------------
# UPLOAD - ERROR PAGES
# -----------------------------------------------------------------------------

@app.route('/too_large_file')
@login_required
def too_large_file():
    return render_template('utils/max_file_size.html')


@app.route('/something_wrong/<page>')
@login_required
def something_wrong(page):
    return render_template('utils/something_wrong.html', page=page)

# =============================================================================
#
#                               ANALYSIS
#
# =============================================================================

@app.route('/analysis/<int:user_id>_<int:study_id>', methods=['GET', 'POST'])
@login_required
def analysis(user_id, study_id):
    """
    Handles the setup of analyses. Just as upload, it uses AJAX POST requests
    to do the server side form validation.
    """
    if not security_check(user_id, study_id):
        abort(403)

    # user cannot submit a new analysis till the previous hasn't finished
    if len(current_user.analyses.filter_by(status=1).all()) > 0:
        return render_template('utils/analysis_in_progress.html')

    # -------------------------------------------------------------------------
    # we got a POST AJAX request from the client
    if request.method == 'POST':
        # rebuild form from request.values and request.files
        form = AnalysisForm(data=get_form(request.values, request.files))
        try:
            check = request.form['check']
            if check == 'true':
                check = True
            else:
                check = False
        except:
            return json.dumps(dict(status='invalid'))

        # ---------------------------------------------------------------------
        # we got a form that needs to be validated
        if check:
            # set global study_id, so form validation can check analysis name
            session['study_id'] = study_id
            if form.validate_on_submit():
                return json.dumps(dict(status='OK'))
            else:
                return json.dumps(dict(status='errors', errors=form.errors))

        # ---------------------------------------------------------------------
        # we got a form, that has passed validation, let's start the analysis
        else:
            try:
                save_analysis(form, study_id)
                task = run_analysis.apply_async(args=[current_user.id], countdown=1)
                # save task id so user can terminate long running jobs
                session['task_id'] = task.id
                return json.dumps(dict(status='OK'))
            except:
                # there was some problem with the saving of the analysis
                return json.dumps(dict(status='invalid'))

    # -------------------------------------------------------------------------
    # render the form for the first time via GET
    else:
        form = AnalysisForm()
        # check how many analyses the current user has
        too_many_analyses = 0
        if len(current_user.analyses.all()) >= app.config['ACTIVE_ANALYSIS_PER_USER']:
            too_many_analyses = 1
        if current_user.num_analyses >= app.config['ANALYSIS_PER_USER']:
            too_many_analyses = 2

        # get vars about study and dashboard cols
        study = models.Studies.query.get(study_id)
        study_name = study.study_name
        return render_template('analysis.html', form=form, user_id=user_id,
                               study_id=study_id, study_name=study_name,
                               too_many_analyses=too_many_analyses)

# =============================================================================
#
#                               PROFILE
#
# =============================================================================

@app.route('/profile')
@login_required
def profile():
    # collect studies from database
    studies_array = get_studies_array()
    # collect analyses from database
    analyses_array = get_analyses_array()
    # user_id and study_id to get results safely
    user_id = current_user.id
    if len(studies_array) > 0:
        study_id = studies_array[0]['id']
    else:
        study_id = 0

    # does user need intro to profile?
    if current_user.profile_intro == 0:
        profile_intro = True
        current_user.profile_intro = 1
        db.session.add(current_user)
        db.session.commit()
    else:
        profile_intro = False

    # stats about number of studies and analyses
    stats = {
        'active_studies': len(current_user.studies.all()),
        'all_studies': current_user.num_studies,
        'active_analyses': len(current_user.analyses.all()),
        'all_analyses': current_user.num_analyses
    }
    return render_template('profile.html', studies=studies_array, stats=stats,
                           analyses=analyses_array, profile_intro=profile_intro,
                           user_id=user_id, study_id=study_id)

# -----------------------------------------------------------------------------
# DELETE STUDY
# -----------------------------------------------------------------------------

@app.route('/delete_study/<int:user_id>_<int:study_id>/', methods=['POST'])
@login_required
def delete_study(user_id, study_id):
    if not security_check(user_id, study_id):
        abort(403)

    # delete study and all linked analyses from database
    study = models.Studies.query.get(study_id)
    study_name = study.study_name
    for analysis in study.analyses.all():
        db.session.delete(analysis)
    db.session.delete(study)
    db.session.commit()

    # delete from file system
    user_folder = get_user_folder()
    study_folder = secure_filename(study_name)
    folder_to_delete = os.path.join(user_folder, study_folder)
    if os.path.exists(folder_to_delete):
        shutil.rmtree(folder_to_delete)
    return redirect(url_for('profile'))

# -----------------------------------------------------------------------------
# DELETE ANALYSIS
# -----------------------------------------------------------------------------

@app.route('/delete_analysis/<int:user_id>_<int:analysis_id>/', methods=['POST'])
@login_required
def delete_analysis(user_id, analysis_id):
    if not security_check(user_id, analysis_id, True):
        abort(403)

    # delete from database, get study folder
    analysis = models.Analyses.query.get(analysis_id)
    status = analysis.status
    analysis_name = analysis.analysis_name
    study_folder = secure_filename(analysis.study.study_name)
    db.session.delete(analysis)
    db.session.commit()

    # stop excecutiong of script
    if status == 1:
        terminate_analysis(session['task_id'])

    # delete from file system
    user_folder = get_user_folder()
    analysis_folder = secure_filename(analysis_name)
    folder_to_delete = os.path.join(user_folder, study_folder, analysis_folder)
    if os.path.exists(folder_to_delete):
        shutil.rmtree(folder_to_delete)
    return redirect(url_for('profile'))

# -----------------------------------------------------------------------------
# GET FILE
# -----------------------------------------------------------------------------

@app.route('/get_file/<int:user_id>_<int:study_id>_<int:analysis>_<path:file>')
@login_required
def get_file(user_id, study_id, analysis, file):
    """
    We need to serve static files (.js, .json) securely for the dashboard and
    visualisations that are not in the default location (i.e. static folder),
    because they are protected and user specific. app.instance_path was set to
    /userData with its absolute path in __init__.py.

    If analysis is True, study_id will be checked as analysis_id.
    """
    if not security_check(user_id, study_id, bool(analysis)):
        abort(403)
    return send_from_directory(app.instance_path, file)

# =============================================================================
#
#                               VIS
#
# =============================================================================

@app.route('/vis/<int:user_id>_<int:analysis_id>_<path:data_file>')
@login_required
def vis(user_id, analysis_id, data_file):
    """
    Displays network visualisation for analysis
    """
    if not security_check(user_id, analysis_id, True):
        abort(403)

    if data_file not in ['dataset1_2', 'dataset1', 'dataset2']:
        abort(403)

    # get study_folder, i.e. location of dashboard.js and dashboard.json
    analysis = models.Analyses.query.get(analysis_id)
    analysis_name = analysis.analysis_name
    study = models.Studies.query.get(analysis.study_id)
    study_name = study.study_name
    username = app.config['USER_PREFIX'] + str(current_user.id)
    analysis_folder = os.path.join(username, secure_filename(study_name),
                                   secure_filename(analysis_name))
    autocorr = bool(study.autocorr)
    dataset_names = [study.dataset1_type]
    if autocorr:
        dataset_names += study.dataset1_type
    else:
        dataset_names += [study.dataset2_type]

    return render_template('vis.html', analysis_folder=analysis_folder,
                           analysis_name=analysis_name, autocorr=autocorr,
                           user_id=user_id, analysis_id=analysis_id,
                           data_file=data_file,
                           dataset_names=dataset_names)

# =============================================================================
#
#                               ERROR PAGES
#
# =============================================================================

@app.errorhandler(403)
def forbidden_error(error):
    app.logger.error('403 - Forbidden request: %s', request.path)
    return render_template('utils/403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    # if an scatter plot is not found that's ok
    if "/get_file/" not in request.path:
        app.logger.error('404 - Page not found: %s', request.path)
    return render_template('utils/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('500 - Internal server error: %s', request.path)
    return render_template('utils/500.html'), 500


@app.errorhandler(500)
def all_exception_error(exception):
    db.session.rollback()
    app.logger.error('All other exception error: %s', request.path)
    return render_template('utils/500.html'), 500


# =============================================================================
#
#                               ROBOTS & SITEMAP
#
# =============================================================================

@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/favicon.ico')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
