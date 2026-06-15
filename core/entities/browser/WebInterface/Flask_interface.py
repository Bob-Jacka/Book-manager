"""
Flask driven web engine
"""
from time import sleep

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify
)

from core.entities.Book_data import Book_data
from core.other import Utils
from data.Wrappers import safe_log

__web_app: Flask = Flask(__name__, static_url_path='/static')


class Dp:
    """
    Static web interface dependencies
    """
    history_mod: None
    transfer_mod: None
    stat_mod: None
    local_logger: None
    config: None


class Cache:
    all_books: list[dict] = None
    fav_books: list[dict] = None
    all_book_count: int = 0
    fav_book_count: int = 0
    found_books: list[str]


@safe_log
def run_web_app():
    """
    Entry point to web interface run
    :return:
    """
    __web_app.run()


##Pages handlers:

@__web_app.route('/', methods=['GET'])
def root_page():
    return render_template('home.html')


@__web_app.route('/add', methods=['GET', 'POST'])
def add_book_page():
    """
    Page for adding book to read history
    :return: page
    """
    if Dp.transfer_mod is None or Dp.history_mod is None:
        flash("Error, transfer or history module is not initialized")
        return redirect(url_for('root_page'))  # go back in case of error

    if request.method == 'POST':
        book: Book_data = Book_data()

        title = request.form.get('title')  # book name
        author = request.form.get('author')  # optional
        book_category = request.form.get('category')  # optional
        book_type = request.form.get('book_type')

        book.set_book_name(title)
        book.set_book_author(author)
        book.set_book_category(book_category)
        book.set_book_type(book_type)

        Dp.history_mod.add_book_to_history(book)
        Dp.local_logger.log(f'Added book data - {book}')

        sleep(1)  # make user feel comfortable, sleep for 1 sec to guarantee work illusion
        return redirect(url_for('root_page'))
    return render_template('add_book.html')


@__web_app.route('/remove', methods=['GET', 'POST'])
def remove_book_page():
    """
    Page for removing book
    :return: page
    """
    if Dp.transfer_mod is None:
        flash("Error, transfer module is not initialized")
        return redirect(url_for('root_page'))

    if request.method == 'POST':
        title = request.form['title']  # required parameter

        sleep(1)  # make user feel comfortable, sleep for 1 sec to guarantee work illusion
        return redirect(url_for('root_page'))
    return render_template('remove_book.html')


@__web_app.route('/find', methods=['GET', 'POST'])
def find_book_data():
    """
    Found or not found book in history and get result
    """
    data = request.get_json()
    text = data.get('text') if data else None
    search_res = Dp.history_mod.find_book(text)
    if Cache.found_books.__contains__(search_res):
        Dp.local_logger.log('Found result in cache')
        return jsonify({'status': 'found', 'message': 'Book found in history'})
    else:
        if search_res:
            Cache.found_books.append(search_res)  # appends only short variant
            return jsonify({'status': 'found', 'message': 'Book found in history'})
        else:
            return jsonify({'status': 'not_found', 'message': 'Book not found in history'})


@__web_app.route('/about', methods=['GET'])
def about_util_page():
    """
    Page with information about utility
    :return: page
    """
    return render_template('about.html')


@__web_app.route('/book', methods=['GET'])
def about_book_page():
    """
    Page with information about selected book
    :return: page
    """
    if Cache.all_books is None:
        books = Dp.history_mod.list_all_read_book()
        Cache.all_books = books
    else:
        books = Cache.all_books
    return render_template('about_book.html', books=books)


@__web_app.route('/book/info', methods=['POST'])
def get_book_info():
    """
    Get detailed information about selected book
    :return: JSON with book data
    """
    data = request.get_json()
    book_name = data.get('book_name') if data else None

    if not book_name:
        return jsonify({'found': False})

    # Find book in cache
    book_data: dict | None = None
    for book in Cache.all_books:
        if book.get('name') == book_name:
            book_data = book
            break

    if not book_data:
        return jsonify({'found': False})

    # Create Book_data object for additional info \ lua methods
    book_obj = Book_data(
        current_storing_dir=Dp.config.get_central_dir_name(),
        book_name=book_data.get('name', ''),
        book_category=book_data.get('category', ''),  # TODO нет там таких данных
        book_type=book_data.get('type', 'text'),
        book_author=book_data.get('author', '')
    )
    Utils.get_book_cover()  # search for book cover

    return jsonify({
        'found': True,
        'name': book_obj.get_book_name(),
        'author': book_obj.get_book_author(),
        'category': book_obj.get_book_category(),
        'type': book_obj.get_book_type(),
        'dir': book_obj.get_current_dir(),
        'full_path': book_obj.get_full_path(),
        'has_bookmark': book_obj.has_bookmark_dir()
    })


@__web_app.route('/actions', methods=['GET'])
def actions_page():
    """
    Page with redirect to add book or delete book
    :return: page
    """
    return render_template('actions.html')


@__web_app.route('/history', methods=['GET'])
def history_page():
    view = request.args.get('view', 'all')

    if view == 'favourites':
        if Cache.fav_books is None:
            books = Dp.history_mod.list_favourite_books()
            book_count = len(books)
            Cache.fav_books = books
            Cache.fav_book_count = book_count
        else:
            Dp.local_logger.log('Using cache value for favourite')
            books = Cache.fav_books
            book_count = len(books)

    elif view == 'all':
        if Cache.all_books is None:
            books = Dp.history_mod.list_all_read_book()
            book_count = len(books)
            Cache.all_books = books
            Cache.all_book_count = book_count
        else:
            Dp.local_logger.log('Using cache value for all books')
            books = Cache.all_books
            book_count = len(books)
    else:
        flash("Error in history module")
        return redirect(url_for('root_page'))
    return render_template('history.html', books=books, book_count=book_count)


@__web_app.route('/stats', methods=['GET'])
def statistics_page():
    """
    Page with reading statistics in form of web
    """
    if Dp.stat_mod is None:
        flash("Error, statistics module is not initialized")
        return redirect(url_for('root_page'))

    if Dp.history_mod is None:
        flash("Error, history module is not initialized")
        return redirect(url_for('root_page'))

    audio_books: int = 0
    categories: dict = {}
    recent_books: list[str] = []

    if Cache.all_book_count == 0 and Cache.fav_book_count == 0:
        data = Dp.history_mod.count_all_books()  # all book list, fav list, count
        total_books_count = data[2]

        Dp.local_logger.log('Update all books and favourite book data')
        Cache.all_books = data[0]
        Cache.fav_books = data[1]
    else:
        Dp.local_logger.log('Using cache total books count')
        total_books_count = Cache.fav_book_count + Cache.all_book_count

    return render_template('statistics.html',
                           total_books=total_books_count,
                           audio_books=audio_books,
                           categories=categories,
                           recent_books=recent_books)


@__web_app.route('/stats/calculate', methods=['POST'])
def calculate_reading_speed():
    """
    Calculate reading speed
    """
    from datetime import datetime
    start_date_str = request.form.get('start_date')
    period = request.form.get('period', 'year')

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        calculated_speed = "..."

    return redirect(url_for('statistics_page'))
