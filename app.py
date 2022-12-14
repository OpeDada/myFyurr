#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from tracemalloc import start
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import  Venue, VenueList, Artist, Show
from app_init import app, db

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = VenueList.query.all()
  return render_template('pages/venues.html',
  areas= data

  )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  #retrieve the search term from the request
  search_term = request.form.get('search_term')

  #do a query filter with it and fetch all records that match the search term
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  #build the response
  response = {}
  response['count'] = len(venues)
  response['data'] = venues

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    data = []
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in shows:
      data = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time))
    }
      if show.start_time > current_time:
        upcoming_shows.append(data)
      else:
        past_shows.append(data)
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres.split(','),
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website' : venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
      }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  venue = VenueForm(request.form)

  validate = venue.validate_on_submit()
  error = False
  body = {}
  if validate:
    try:
      form_data = dict(request.form)
      name = form_data['name']
      genres = ",".join(venue.genres.data)
      city = form_data['city']
      state = form_data['state']
      address = form_data['address']
      phone = form_data['phone']
      image_link = form_data['image_link']
      facebook_link = form_data['facebook_link']
      website = form_data['website_link']
      seeking_talent = False if form_data.get("seeking_talent", None) is None else True
      seeking_description = form_data['seeking_description']
      avail_v_list = Venue.query.filter_by(city=city, state=state).first()
      app.logger.info(f'avail_v_list: ,{avail_v_list}')

      if avail_v_list is None:
        avail_v_list = VenueList(city=city, state=state)
        db.session.add(avail_v_list)
        db.session.commit()
        v_list_id = avail_v_list.id
      else:
        v_list_id = avail_v_list.vList_id

      venue = Venue(name=name, genres=genres, city=city,
      state=state, address=address, phone=phone, image_link=image_link,
      facebook_link=facebook_link, website=website, seeking_talent=seeking_talent,
      seeking_description=seeking_description, vList_id=v_list_id)

      db.session.add(venue)
      db.session.commit()

      body['name'] = venue.name
      body['genres'] = venue.genres
      body['city'] = venue.city
      body['state'] = venue.state
      body['address'] = venue.address
      body['phone'] = venue.phone
      body['image_link'] = venue.image_link
      body['facebook_link'] = venue.facebook_link
      body['website'] = venue.website
      body['seeking_talent'] = venue.seeking_talent
      body['seeking_description'] = venue.seeking_description
      body['vList_id'] = venue.vList_id

    except Exception as e:
      app.logger.error(f"Error: {e}")
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      if error:
        flash('Venue ' + request.form['name'] + ' was not successfully listed!')
        abort (400)
      else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

  else:
        flash('Venue ' + request.form['name'] + ' was not successfully listed!')

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    curr_venue = Venue.query.filter_by(id=venue_id)
    v_list_len = len(Venue.query.filter_by(vList_id=curr_venue.first().vList_id).all())
    v_list = VenueList.query.filter_by(id=curr_venue.first().vList_id)
    curr_venue.delete()

    app.logger.info(f"v list len: {v_list_len}")
    app.logger.info(f"v list: {v_list.first().venues}")
    if v_list_len <= 1:
      v_list.delete()
    db.session.commit()
  except Exception as e :
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  data = VenueList.query.all()
  return render_template('pages/venues.html',
  areas= data

  )

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  #retrieve the search term from the request
  search_term = request.form.get('search_term')

  #do a query filter with it and fetch all records that match the search term
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  #build the response
  response = {}
  response['count'] = len(artists)
  response['data'] = artists

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id


    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    data = []
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in shows:
      data = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': format_datetime(str(show.start_time))
    }
      if show.start_time > current_time:
        upcoming_shows.append(data)
      else:
        past_shows.append(data)
    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres.split(','),
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website' : artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
      }


    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    phone=artist.phone,
    genres=artist.genres.split,
    facebook_link=artist.facebook_link,
    image_link=artist.image_link,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description,
    website=artist.website
  )
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist_form = ArtistForm(request.form)
  validate = artist_form.validate_on_submit()

  if validate:
    try:
      artist.name = artist_form.name.data
      artist.genres = ",".join(artist_form.genres.data)
      artist.city = artist_form.city.data
      artist.state = artist_form.state.data
      artist.phone = artist_form.phone.data
      artist.image_link = artist_form.image_link.data
      artist.facebook_link = artist_form.facebook_link.data
      artist.website_link = artist_form.website_link.data
      artist.seeking_venue = artist_form.seeking_venue.data
      artist.seeking_description = artist_form.seeking_description.data
      db.session.commit()
      db.session.close()
    except:
      db.session.rollback()
    finally:
        db.session.close()
        flash('Artist was successfully updated!')
  else:
        flash('Artist could not be updated ???? ')


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)

  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    address=venue.address,
    phone=venue.phone,
    genres=venue.genres,
    facebook_link=venue.facebook_link,
    image_link=venue.image_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description,
    website=venue.website
  )
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  venue_form = VenueForm()
  validate = venue_form.validate_on_submit()
  if validate:
    try:
      venue.name = venue_form.name.data
      venue.genres = ",".join(venue_form.genres.data)
      venue.city = venue_form.city.data
      venue.state = venue_form.state.data
      venue.address = venue_form.address.data
      venue.phone = venue_form.phone.data
      venue.image_link = venue_form.image_link.data
      venue.facebook_link = venue_form.facebook_link.data
      venue.website_link = venue_form.website_link.data
      venue.seeking_talent = venue_form.seeking_talent.data
      venue.seeking_description = venue_form.seeking_description.data
      app.logger.info(f"venue.seeking description = {venue.seeking_description}")
      db.session.commit()
      db.session.close()
    except:
      db.session.rollback()
    finally:
      db.session.close()
      flash('Venue was successfully updated!')
  else:
      flash('Venue could not be updated ???? ')

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  form = ArtistForm(request.form)

  validate = form.validate_on_submit()

  if validate:
    error = False
    body = {}
    try:
      form_data = dict(request.form)
      name = form_data['name']
      genres = ",".join(form.genres.data) # form_data['genres']
      city = form_data['city']
      state = form_data['state']
      phone = form_data['phone']
      image_link = form_data['image_link']
      facebook_link = form_data['facebook_link']
      website = form_data['website_link']
      seeking_venue = False if form_data.get("seeking_venue", None) is None else True
      seeking_description = form_data['seeking_description']


      artist = Artist(name=name, genres=genres, city=city,
      state=state, phone=phone, image_link=image_link,
      facebook_link=facebook_link, website=website, seeking_venue=seeking_venue,
      seeking_description=seeking_description)

      db.session.add(artist)
      db.session.commit()

      body['name'] = artist.name
      body['genres'] = artist.genres
      body['city'] = artist.city
      body['state'] = artist.state
      body['phone'] = artist.phone
      body['image_link'] = artist.image_link
      body['facebook_link'] = artist.facebook_link
      body['website'] = artist.website
      body['seeking_venue'] = artist.seeking_venue
      body['seeking_description'] = artist.seeking_description

    except Exception as e:
      app.logger.error(f"Error: {e}")
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      if error:
        flash('Artist ' + request.form['name'] + ' was not successfully listed!')
        abort (400)
      else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
        flash('Artist ' + request.form['name'] + ' was not successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time":  show.start_time
  })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  show = ShowForm(request.form)
  validate = show.validate_on_submit()
  error = False
  body = {}
  if validate:
    try:
      form_data = dict(request.form)
      artist_id = form_data['artist_id']
      venue_id = form_data['venue_id']
      start_time = form_data['start_time']
      # format_datetime(str(show.start_time))

      show=Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()

      body['artist_id'] = show.artist_id
      body['venue_id '] = show.venue_id
      body['start_time'] = show.start_time

    except Exception as e:
      app.logger.error(f"Error: {e}")
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      if error:
        flash('An error occurred. Show could not be listed.')
        abort (400)
      else:
        flash('Show was successfully listed!')
  else:
        flash('Show could not be listed!')

  return redirect(url_for('shows'))

      # return render_template('pages/home.html')

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
