###########################
# AUTHORIZATION FUNCTIONS #
#        NOT USED         #
###########################

def auth_user(login, password):
    """
    get user login and password, handle and return session hash
    :param login: user login
    :param password: user password
    :return: session_hash or "session_hash: {error}"
    error: "login error" or "password error"
    """

    isValidSignIn = check_user_sign_in()


def check_user_sign_in():
    return True
