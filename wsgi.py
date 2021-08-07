from src.app import app

if __name__ == "__main__":
    ####################
    # FOR DEVELOPMENT
    ####################
    app.run(host='0.0.0.0', port=9995, debug=True)
