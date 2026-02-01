from flask import Flask, render_template, request
import joblib
import numpy as np

# Load saved objects
popular_df = joblib.load(open('Notebooks/popular_df.pkl', 'rb'))
similarity_scores = joblib.load(open('Notebooks/similarity_scores.pkl', 'rb'))
books_df = joblib.load(open('Notebooks/books_df.pkl', 'rb'))
book_user_matrix = joblib.load(open('Notebooks/book_user_matrix.pkl', 'rb'))

# Normalize index once
book_user_matrix.index = book_user_matrix.index.str.lower()
books_df['Book-Title'] = books_df['Book-Title'].str.lower()

app = Flask(__name__, template_folder="templates")


@app.route('/')
def home():
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['No_Of_Ratings'].values),
        rating=list(popular_df['Avg_Ratings'].values)
    )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    if not user_input:
        return render_template(
            'recommend.html',
            error="Please enter a book name."
        )

    user_input = user_input.strip().lower()

    # Validate input
    if user_input not in book_user_matrix.index:
        return render_template(
            'recommend.html',
            error="Book not found. Please try another book."
        )

    index = np.where(book_user_matrix.index == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:5]

    data = []
    for i in similar_items:
        temp_df = books_df[books_df['Book-Title'] == book_user_matrix.index[i[0]]]

        item = [
            temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0].title(),
            temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0],
            temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]
        ]
        data.append(item)

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
