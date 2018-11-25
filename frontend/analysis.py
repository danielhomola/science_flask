import os
import zipfile
import shutil
import traceback
from celery.exceptions import Terminated
from flask_mail import Message

from backend.corr import corr
from backend.corr import top_var
from backend.utils import io_params
from frontend import app, db, models, create_celery_app, mail

celery = create_celery_app()
# have to set ADMIN config param here, because it would clash with Flask-Mail's
# you need to change this to your admin email address.
celery.conf.ADMINS = [('ScienceFlask', 'admin@scienceflask.com')]


@celery.task(throws=(Terminated,), name='frontend.analysis.run_analysis')
def run_analysis(current_user_id):
    with celery.app.app_context():

        # ----------------------------------------------------------------------
        # LOAD STUDY AND ANALYSIS VARIABLES
        # ----------------------------------------------------------------------
        app_name = app.config['APP_NAME']

        user = models.User.query.get(current_user_id)
        analysis = user.analyses.filter_by(status=1).first()
        analysis_id = analysis.id
        study = models.Studies.query.get(analysis.study_id)

        # get folders of the analysis - this is needed for load_params
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'],
                                   app.config['USER_PREFIX'] +
                                   str(current_user_id))
        study_folder = os.path.join(user_folder, study.study_name)
        analysis_folder = os.path.join(study_folder, analysis.analysis_name)

        # load params file as a dict and define folders from it
        params = io_params.load_params(analysis_folder)
        analysis_folder = params['analysis_folder']
        output_folder = params['output_folder']
        failed_folder = app.config['FAILED_FOLDER']

        # ----------------------------------------------------------------------
        # TOP VARIANCE FEATURES
        # ----------------------------------------------------------------------

        try:
            params = top_var.top_variance(params)
            # if we exited gracefully, just let the user know
            if not params['fs_done']:
                delete_analysis(analysis_id, analysis_folder, failed_folder)
                subject = 'Your CorrMapper job could not be completed'
                message = \
                    ('Your analysis (named: %s) could not be completed '
                     'because could not select the chosen number  of top '
                     'variance features from your datasets. \n\n You can try to'
                     'upload a different dataset or choose a different number '
                     'for top variance in the analysis submission form.'
                     '\n%s Team' % analysis.analysis_name, app_name, )
                send_mail(user.email, user.first_name, analysis.analysis_name,
                          subject, message)
                return False
        except:
            # if something unexpected happened, notify the admins and send the
            # traceback + save the analysis to failedAnalyses folder
            delete_analysis(analysis_id, analysis_folder, failed_folder)
            send_fail_mail(user.email, user.first_name, analysis.analysis_name)
            app.logger.error('Top variance failed for analysis: %d'
                             '\n%s' % (analysis_id, traceback.format_exc()))
            return False

        # ----------------------------------------------------------------------
        # CALCULATE CORR NETWORK, P-VALUES, WRITE JS VARS AND DATA FOR VIS
        # ----------------------------------------------------------------------

        try:
            params = corr.corr_main(params)
            if not params['corr_done']:
                delete_analysis(analysis_id, analysis_folder, failed_folder)
                subject = 'Your %s job could not be completed' % app_name
                message = \
                    ('Your analysis (named: %s) could not be completed '
                     'because one of the correlation matrices returned by the'
                     'GLASSO algorithm is empty. This could happen if you have'
                     'very few samples, select overly harsh p-value cut-off, or'
                     'the selected feature selection algorithm did not find'
                     'enough relevant features.\n\n You can try to run '
                     '%s with a different metadata variable, feature '
                     'selection method, or dataset.'
                     '\n%s Team'
                     % analysis.analysis_name, app_name, app_name)
                send_mail(user.email, user.first_name, analysis.analysis_name,
                          subject, message)
                return False
        except:
            delete_analysis(analysis_id, analysis_folder, failed_folder)
            send_fail_mail(user.email, user.first_name, analysis.analysis_name)
            app.logger.error('Correlation calculation failed for analysis: %d'
                             '\n%s' % (analysis_id, traceback.format_exc()))
            return False

        # ----------------------------------------------------------------------
        # ZIP RESULTS FOLDER, DELETE OUTPUT FOLDER
        # ----------------------------------------------------------------------

        try:
            zip_study(analysis.analysis_name, analysis_folder, output_folder)
        except:
            delete_analysis(analysis_id, analysis_folder, failed_folder)
            send_fail_mail(user.email, user.first_name, analysis.analysis_name)
            app.logger.error('Making zip from output failed for analysis: %d'
                             '\n%s' % (analysis_id, traceback.format_exc()))
            return False
        # ----------------------------------------------------------------------
        # SAVE PARAMS, SEND EMAIL
        # ----------------------------------------------------------------------

        try:
            io_params.write_params(analysis_folder, params)
            send_mail(user.email, user.first_name, analysis.analysis_name)
            analysis.status = 2
            db.session.commit()
            return True
        except:
            delete_analysis(analysis_id, analysis_folder, failed_folder)
            send_fail_mail(user.email, user.first_name, analysis.analysis_name)
            app.logger.error('End of pipeline failed for analysis: %d'
                             '\n%s' % (analysis_id, traceback.format_exc()))
            return False


def send_fail_mail(email, first_name, analysis_name):
    app_name = app.config['APP_NAME']
    subject = 'Your %s job could not be completed' % app_name
    message = ('Your analysis (named: %s) encountered a bug in our system and'
               ' could not be completed. We received a report of this and will'
               ' get back to you once we fixed the issue. Until then, you can'
               ' try to run %s with a different metadata variable,'
               ' feature selection method, or dataset.\n\nThank you for your'
               ' understanding!\n\n%s Team' % (analysis_name, app_name, app_name))
    send_mail(email, first_name, analysis_name, subject, message)


def send_mail(email, first_name, analysis_name, subject=None, message=None):
    app_name = app.config['APP_NAME']
    # default success message
    if message == None:
        subject = ('Your %s job finished' % app_name)
        message = ('Your analysis (named: %s) has finished running. '
                  'You can check the results in your profile under the Analyses'
                  ' tab. \n%s Team' % (analysis_name, app_name))

    msg = Message(subject, recipients=[email])
    if first_name is None:
        hi = 'Hi,\n\n'
    else:
        hi = 'Hi %s, \n\n' % first_name
    msg.body = (hi + message)
    mail.send(msg)


def zip_study(analysis_name, analysis_folder, output_folder):
    """
    Writes a .zip file from the output folder and deletes the output_folder
    """
    zip_path = os.path.join(analysis_folder, analysis_name + '.zip')
    zipf = zipfile.ZipFile(zip_path , 'w', zipfile.ZIP_DEFLATED)
    of_len = len(output_folder) + 1
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, file_path[of_len:])
    zipf.close()

    # if os.path.exists(output_folder):
    #     shutil.rmtree(output_folder)


def terminate_analysis(task_id):
    """
    Kills running analysis if the users deletes it from profile
    """
    try:
        celery.control.revoke(task_id, terminate=True)
    except Terminated:
        pass


def delete_analysis(analysis_id, analysis_folder, failed_folder):
    # delete from database, get study folder
    analysis = models.Analyses.query.get(analysis_id)
    db.session.delete(analysis)
    db.session.commit()
    # move analysis folder to failed folder so we can debug it later
    failed_path = os.path.join(failed_folder, 'failed_' + str(analysis_id))
    # if a failed analysis with this id already exist try again till we are ok
    if os.path.exists(failed_path):
        counter = 1
        failed_path = os.path.join(failed_folder, 'failed_' + str(analysis_id)
                                   + '_' + str(counter))
        while os.path.exists(failed_path):
            counter += 1
            failed_path = os.path.join(failed_folder,
                                       'failed_' + str(analysis_id)
                                       + '_' + str(counter))
    shutil.copytree(analysis_folder, failed_path)
    # delete analysis folder from user folder
    if os.path.exists(analysis_folder):
        shutil.rmtree(analysis_folder)
