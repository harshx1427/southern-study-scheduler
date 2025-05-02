from flask import Blueprint, render_template, redirect
def form():
    return render_template_string(form_template)

@app.route('/submit', methods=['POST'])
def submit():
    subject = request.form['subject']
    datetime = request.form['datetime']
    location = request.form['location']
    description = request.form['description']


if __name__ == '__main__':
    app.run(debug=True)