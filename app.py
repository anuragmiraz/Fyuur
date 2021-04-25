#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# My change starts
from flask_migrate import Migrate
import sys
from datetime import datetime
# My change ends

# #----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# My change starts
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:doublea@localhost:5432/fyuur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# My change ends

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
# My change starts
  data=[]
  city_state = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for i in city_state:
    venue_details=[]
    venue_name = Venue.query.filter_by(city = i.city).filter_by(state = i.state).all()
    for j in venue_name:
      venue_details.append({
        "id": j.id,
        "name": j.name,
        "num_upcoming_shows": Shows.query.filter(Shows.venue_id==j.id, Shows.start_time > datetime.now()).count()
# cant see if above query output is used anywhere 
      })
    data.append({
        "city": i.city, 
        "state": i.state, 
        "venues": venue_details
    })
# My change ends
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
# My change starts
  input_data = request.form.get('search_term', '')
  venue_data = []
  response = []
  table_data = Venue.query.filter(Venue.name.ilike('%' + input_data + '%')).all()
  for i in table_data:
    venue_data.append({
      "id": i.id, 
      "name": i.name, 
      "num_upcoming_shows": Shows.query.filter(Shows.venue_id==i.id, Shows.start_time > datetime.now()).count()
    })
  response = {
    "count": len(venue_data),
    "data": venue_data
    }
# My change ends
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
# My change starts
  data=[]
  past_show_details=[]
  upcoming_show_details=[]
  past_shows = Shows.query.filter(Shows.venue_id==venue_id, Shows.start_time < datetime.now()).all()
  for i in past_shows:
    some_data = Artist.query.filter(Artist.id == i.artist_id).all()
    past_show_details.append({
        "artist_id": i.artist_id, 
        "artist_name": i.Artist.name, 
        "artist_image_link": i.Artist.image_link,
        "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  upcoming_shows = Shows.query.filter(Shows.venue_id==venue_id, Shows.start_time > datetime.now()).all()
  for j in upcoming_shows:
    new_data = Artist.query.filter(Artist.id == j.artist_id).all()
    upcoming_show_details.append({
        "artist_id": j.artist_id, 
        "artist_name": j.Artist.name, 
        "artist_image_link": j.Artist.image_link,
        "start_time": j.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  venue_details = Venue.query.get(venue_id)
  data = {
        "id": venue_details.id,
        "name": venue_details.name,
        "address": venue_details.address,
        "city": venue_details.city,
        "state": venue_details.state,
        "phone": venue_details.phone,
        "website": venue_details.website_link,
        "facebook_link": venue_details.facebook_link,
        "seeking_talent": venue_details.seeking_talent,
        "seeking_description": venue_details.seeking_description,
        "image_link": venue_details.image_link,
        "past_shows": past_show_details,
        "upcoming_shows": upcoming_show_details,
        "past_shows_count": len(past_show_details),
        "upcoming_shows_count": len(upcoming_show_details)
        }

#  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
# My change ends     
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
# My change starts
    error = False
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      genres = request.form.getlist('genres')
      website_link = request.form.get('website_link')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')
      venue_record = Venue(name=name, city=city, state=state, address=address, phone=phone, 
      image_link=image_link, facebook_link=facebook_link, genres=genres, website_link=website_link, 
      seeking_talent=seeking_talent, seeking_description=seeking_description)
      db.session.add(venue_record)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      error = True
      db.session.rollback()
      flash('Venue ' + request.form['name'] + ' could not be listed!')
      print(sys.exc_info())
    finally:
      db.session.close()
# My change ends
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
# My change starts
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    error = True
    db.session.rollback()
    flash('Venue could not be deleted!')
    print(sys.exc_info())
  finally:
    db.session.close()
# My change ends  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
# My change starts
  data=Artist.query.all()
# My change ends  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
# My change starts
  input_data = request.form.get('search_term', '')
  artist_data = []
  response = []
  table_data = Artist.query.filter(Artist.name.ilike('%' + input_data + '%')).all()
  for i in table_data:
    artist_data.append({
      "id": i.id,
      "name": i.name,
      "num_upcoming_shows": Shows.query.filter(Shows.artist_id==i.id, Shows.start_time > datetime.now()).count()
    })
  response = ({
    "count": len(artist_data),
    "data": artist_data
    })
# My change ends
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # My change starts
  data=[]
  past_show_details=[]
  upcoming_show_details=[]
  past_shows = Shows.query.filter(Shows.artist_id==artist_id, Shows.start_time < datetime.now()).all()
  for i in past_shows:
    some_data = Venue.query.filter(Venue.id == i.venue_id).all()
    past_show_details.append({
        "venue_id": i.venue_id,
        "venue_name": i.Venue.name,
        "venue_image_link": i.Venue.image_link,
        "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  upcoming_shows = Shows.query.filter(Shows.artist_id==artist_id, Shows.start_time > datetime.now()).all()
  for j in upcoming_shows:
    new_data = Venue.query.filter(Venue.id == j.venue_id).all()
    upcoming_show_details.append({
        "venue_id": j.venue_id,
        "venue_name": j.Venue.name,
        "venue_image_link": j.Venue.image_link,
        "start_time": j.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  artist_details = Artist.query.get(artist_id)
  data = {
        "id": artist_details.id,
        "name": artist_details.name,
        "genres": artist_details.genres,
        "city": artist_details.city,
        "phone": artist_details.phone,
        "state": artist_details.state,
        "website": artist_details.website_link,
        "facebook_link": artist_details.facebook_link,
        "seeking_venue": artist_details.seeking_venue,
        "seeking_description": artist_details.seeking_description,
        "image_link": artist_details.image_link,
        "past_shows": past_show_details,
        "upcoming_shows": upcoming_show_details,
        "past_shows_count": len(past_show_details),
        "upcoming_shows_count": len(upcoming_show_details)
        }

# data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
# My change ends     
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

# ???????????????????
# Open Query / Todo - Why the form is not populating old detials while sending editable screen
# ???????????????????

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # My Change starts
  artist=Artist.query.get(artist_id)
  # My Change ends
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
# My Change starts
    error = False
    try:
      upd_artist = Artist.query.get(artist_id)
      upd_artist.name = request.form.get('name')
      upd_artist.city = request.form.get('city')
      upd_artist.state = request.form.get('state')
      upd_artist.phone = request.form.get('phone')
      upd_artist.genres = request.form.getlist('genres')
      upd_artist.image_link = request.form.get('image_link')
      upd_artist.facebook_link = request.form.get('facebook_link')
      upd_artist.website_link = request.form.get('website_link')
      upd_artist.seeking_venue = request.form.get('seeking_venue', 'N')
      upd_artist.seeking_description = request.form.get('seeking_description')
      db.session.commit()
      flash('Artist was successfully updated!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('Artist details could not be updated!')
    finally:
      db.session.close()
# My Change ends
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # My Change starts
  venue=Venue.query.get(venue_id)
  # My Change ends
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
# My Change starts
    error = False
    try:
      upd_venue = Venue.query.get(venue_id)
      upd_venue.name = request.form.get('name')
      upd_venue.city = request.form.get('city')
      upd_venue.state = request.form.get('state')
      upd_venue.address = request.form.get('address')
      upd_venue.phone = request.form.get('phone')
      upd_venue.image_link = request.form.get('image_link')
      upd_venue.facebook_link = request.form.get('facebook_link')
      upd_venue.genres = request.form.getlist('genres')
      upd_venue.website_link = request.form.get('website_link')
      upd_venue.seeking_talent = request.form.get('seeking_talent', 'N')
      upd_venue.seeking_description = request.form.get('seeking_description')
      db.session.commit()
      flash('Venue was successfully updated!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue details could not be updated!')
    finally:
      db.session.close()
# My Change ends
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
# My change starts
    error = False
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      image_link = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_venue = request.form.get('seeking_venue')
      seeking_description = request.form.get('seeking_description')
      artist_record = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
      image_link=image_link, facebook_link=facebook_link, website_link=website_link, 
      seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(artist_record)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      error = True
      db.session.rollback()
      flash('Artist ' + request.form['name'] + ' could not be listed!')
      print(sys.exc_info())
    finally:
        db.session.close()
# My change ends
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
# My change starts
  shows_output = Shows.query.join(Artist).join(Venue).order_by(db.asc(Shows.start_time)).all()
  data = []
  for k in shows_output:
    data.append({
      "venue_id": k.venue_id,
      "venue_name": k.Venue.name,
      "artist_id": k.artist_id,
      "artist_name": k.Artist.name,
      "artist_image_link": k.Artist.image_link,
      "start_time": k.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
# My change ends     
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
# My change starts
    error = False
    try:
      venue_id = request.form.get('venue_id')
#      venue_name = Venue.query.get(Venue.name).filter_by(id=venue_id)
      artist_id = request.form.get('artist_id')
#      artist_name = Artist.query.get(Artist.name).filter_by(id=artist_id)
      start_time = request.form.get('start_time')
      show_record = Shows(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
#      show_record = Shows(venue_id=venue_id, venue_name=venue_name, artist_id=artist_id, artist_name=artist_name,
#      start_time=start_time)
      db.session.add(show_record)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      error = True
      db.session.rollback()
      flash('Show could not be listed!')
      print(sys.exc_info())
    finally:
        db.session.close()
# My change ends
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
