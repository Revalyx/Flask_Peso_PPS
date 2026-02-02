from src.app import app

if __name__ == '__main__':
    # TIENE QUE SER 5000
    app.run(host='0.0.0.0', port=5000, debug=True)