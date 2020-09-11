from configupdater import ConfigUpdater
from heliopy.util.config import get_config_file


def set_load_config(database_path = None, cluster_cookie=None):
    """
    Help to set the mission data loading.

    Parameters
    ----------
    database_path : str
        Absolute path where to save all the downloaded files.
        It not, the default path is ~/heliopy/

    cluster_cookie : str
        Cookie from ESA to download cluster data.
    """
    #Get the path of heliopyrc file
    config_path = get_config_file()
    
    # Read the preexisting config file using configupdater
    config = ConfigUpdater()
    config.read(config_path)

    # Set new data download directory if passed
    if database_path:
        config['DEFAULT']['download_dir'].value = database_path

    # Set new cluster cookie if passed
    if cluster_cookie:
        config['DEFAULT']['cluster_cookie'].value = cluster_cookie

    # Update the config file with new entries
    config.update_file()
