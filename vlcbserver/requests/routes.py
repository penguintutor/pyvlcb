import time
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from strip_tags import strip_tags
#from flask import Markup
import threading
import logging, os
import vlcbserver
#from pixelserver.statusmsg import StatusMsg
#from pixelserver.serverauth import ServerAuth
#from pixelserver.serveruseradmin import ServerUserAdmin

from . import requests_blueprint

@requests_blueprint.route("/")
def test():
    return "Test data"

@requests_blueprint.route("/vlcb")
def vlcb_request():
    # If there is a value then it's a send
    this_arg = request.args.get('send', default = 'none', type = str)
    if this_arg != "none":
        #print (f"Send {this_arg}")
        #Todo check valid format
        vlcbserver.send_data(this_arg)
        return_data = ["0,0,0"]
        
    else:
        this_arg = request.args.get('read', default = 0, type = int)
        #print (f"Read {this_arg}")
        entries = vlcbserver.get_data(this_arg)
        # Add first entry
        return_data = entries[0]
        for i in range(1, len(entries)):
            return_data += "\n"
            return_data += entries[i]
    #return (vlcbserver.data)
    return return_data
    
#/vlcb?read=<id of first data packet>&format=txt&[&end=<id last packet to retrieve]
#/vlcb?send=<string of send request>&format=txt

#@requests_blueprint.route("/")
@requests_blueprint.route("/home")
def main():
    login_status = 'logged_in'
    #ip_address = get_ip_address()
    #login_status = pixelserver.auth.auth_check(ip_address, session)
    # not allowed even if logged in
    if login_status == "invalid":
        return redirect('/invalid')
    elif login_status == "network":
        return render_template('index.html', user="guest", admin=False)
    elif login_status == "logged_in":
        # Also check if admin - to show settings button
        username = session['username']
        if (pixelserver.auth.check_admin(username)):
            admin = True
        else:
            admin = False
        return render_template('index.html', user=session['username'], admin=admin)
    else:   # login required
        return redirect('/login')

@requests_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    # Start by setting ip address to the real address
    ip_address = get_ip_address()
    login_status = pixelserver.auth.auth_check(ip_address, session)
    # check not an unauthorised network
    if login_status == "invalid":
        return redirect('/invalid')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (pixelserver.auth.login_user(username, password, ip_address) == True):
            # create session
            session['username'] = username
            return redirect('/')
        return render_template('login.html', message='Invalid login attempt')
    # New visit to login page
    # Check if user file exists, otherwise give warning message
    # If another error is received then that will override this, but should not be
    # an issue as this warning should only ever be seen on first attempt before
    # users.cfg is created.
    if (not pixelserver.auth.user_file_exists):
        return render_template('login.html', message='No users defined or missing users file. Run createadmin.py through the shell to setup an admin user.')
    else:
        return render_template('login.html')
    
@requests_blueprint.route("/logout")
def logout():
    if 'username' in session:
        username = session['username']
        logging.info("User logged out "+username)
    # pop off the session even if not logged in
    session.pop('username', None)
    return render_template('login.html', message="Logged out")
    
# admin and settings only available to logged in users regardless of 
# network status
@requests_blueprint.route("/settings", methods=['GET', 'POST'])
def settings():
    authorized = pixelserver.auth.check_permission_admin (get_ip_address(), session)
    if authorized != 'admin':
        if (authorized == "invalid"):
            # not allowed even if logged in
            return redirect('/invalid')
        # needs to login
        if (authorized == "login"):
            return redirect('/login')
        # Last option is "notadmin"
        # If trying to do admin, but not an admin then we log them off
        # before allowing them to login again
        session.pop('username', None)
        return render_template('login.html', message='Admin permissions required')
    
    # Reach here logged in as an admin user - update settings and/or display setting options
    username = session['username']
    status_msg = ""
    
    if request.method == 'POST':
        
        update_dict = {}
        
        # process the form - validate all parameters
        # Read into separate values to validate all before updating
        for key, value in request.form.items():
            # skip csrf token
            if key == "csrf_token":
                continue
            (status, temp_value) = pixelserver.pixel_conf.validate_parameter(key, value)
            # If we get an error at any point - don't save and go back to 
            # showing current status
            if (status == False):
                status_msg = temp_value
                break
            # Save this for updating values - use returned value
            # in case it's been sanitised (only certain types are)
            update_dict[key] = temp_value
            
        # special case any checkboxes are only included if checked
        if not ("ledinvert" in request.form.keys()):
            update_dict["ledinvert"] = False
            
                
        # As long as no error save
        if (status_msg == ""):
            for key,value in update_dict.items():
                if (pixelserver.pixel_conf.update_parameter(key, value) == False): 
                    status_msg = "Error updating settings"
                    logging.info("Error updating settings by "+username)
                    
        # Check no error and if so then save
        if not pixelserver.pixel_conf.save_settings():
            status_msg = "Error saving custom config file"
            logging.info("Error saving custom config file")
            
                    
        # As long as still no error then report success
        if (status_msg == ""):
            status_msg = "Updates saved"
            logging.info("Settings updated by "+username)
            
    
    settingsform = pixelserver.pixel_conf.to_html_form()
    # This passes html to the template so turn off autoescaping in the template eg. |safe
    return render_template('settings.html', user=username, admin=True, form=settingsform, message=status_msg)


# profile - can view own profile and change password etc
@requests_blueprint.route("/profile", methods=['GET', 'POST'])
def profile():
    ip_address = get_ip_address()
    # Status msg for feedback to user
    status_msg = ""
    # Authentication first
    login_status = pixelserver.auth.auth_check(ip_address, session)
    # not allowed even if logged in
    if login_status == "invalid":
        return redirect('/invalid')
    # Network approval not sufficient for profile - must be logged in
    # If not approved then issue login page
    if not (login_status == "logged_in") :
        return redirect('/login')
    # Reach here then this is logged in
    username = session['username']
    #get any messages
    status_msg = ""
    if 'msg' in request.args.keys():
        status_msg = request.args['msg']
        # strip tags from status message
        status_msg = strip_tags(status_msg)
        #status_msg = Markup(status_msg).striptags()
    # Create user_admin object as needed shortly
    #user_admin = ServerUserAdmin(pixelserver.auth_users_filename, pixelserver.pixel_conf.get_value('algorithm'))
    # get admin to determine if settings menu is displayed
    is_admin = pixelserver.auth.check_admin(username)
    profile_form = user_admin.html_view_profile(username)
    return render_template('profile.html', user=username, admin=is_admin, form=profile_form, message=status_msg)

@requests_blueprint.route("/password", methods=['GET', 'POST'])
def password():
    ip_address = get_ip_address()
    # Status msg for feedback to user
    status_msg = ""
    # Authentication first
    login_status = pixelserver.auth.auth_check(ip_address, session)
    # not allowed even if logged in
    if login_status == "invalid":
        return redirect('/invalid')
    # Network approval not sufficient for profile - must be logged in
    # If not approved then issue login page
    if not (login_status == "logged_in") :
        return redirect('/login')
    # Reach here then this is logged in
    username = session['username']
    # logged in and have username so allow to change password
    user_admin = ServerUserAdmin(pixelserver.auth_users_filename, pixelserver.pixel_conf.get_value('algorithm'))
    # Is user admin - check for top menu only doesn't change what can be done here
    is_admin = pixelserver.auth.check_admin(username)
    password_form = user_admin.html_change_password()
    if request.method == 'POST':
        # first check existing password
        if (not 'currentpassword' in request.form):
            return render_template('password.html', user=username, admin=is_admin, form=password_form, message="Invalid request")
        if (not user_admin.check_username_password(username, request.form['currentpassword'])):
            return render_template('password.html', user=username, admin=is_admin, form=password_form, message="Incorrect username / password")
        # Now check that repeat is same
        if (not 'newpassword' in request.form) or (not 'repeatpassword' in request.form) or request.form['newpassword'] != request.form['repeatpassword']:
            return render_template('password.html', user=username, admin=is_admin, form=password_form, message="New passwords do not match")
        new_password = request.form['newpassword']
        # check password is valid (meets rules)
        result = user_admin.validate_password(new_password)
        if result[0] != True:
            return render_template('password.html', user=username, admin=is_admin, form=password_form, message=result[1])
        # passed tests so set new password
        user_admin.change_password(username, new_password)
        user_admin.save_users()
        logging.info("Password changed by "+username)
        # redirects to profile
        return redirect('profile?msg=Password changed')
        
    else:
        return render_template('password.html', user=username, admin=is_admin, form=password_form)
    
@requests_blueprint.route("/newuser", methods=['GET', 'POST'])
def newuser():
    authorized = pixelserver.auth.check_permission_admin (get_ip_address(), session)
    if authorized != 'admin':
        if (authorized == "invalid"):
            # not allowed even if logged in
            return redirect('/invalid')
        # needs to login
        if (authorized == "login"):
            return redirect('/login')
        # Last option is "notadmin"
        # If trying to do admin, but not an admin then we log them off
        # before allowing import time
