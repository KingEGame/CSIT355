from web import create_app

# Create the Flask application for the CLI
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 