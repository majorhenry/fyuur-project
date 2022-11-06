#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import sys
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, dataponse, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import null
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# : connect to a local postgdataql database
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
# DELETEING.
#----------------------------------------------------------------------------#

# def clear_tables(model,row_id):
#   if model == 'venue':
#     venue = Venue.query.get(row_id).delete()
#     artist = Artist.query.filter_by(show)
#     show = Show.query.filter_by(venue_id=row_id).delete()
#   elif model == 'show':
#     venue = Venue.query.get(row_id).delete()
#     artist = Artist.query.filter_by(show)
#     show = Show.query.filter_by(venue_id=row_id).delete()
#   elif model == 'artist':
#     venue = Venue.query.get(row_id).delete()
#     artist = Artist.query.filter_by(show)
#     show = Show.query.filter_by(venue_id=row_id).delete()
#   else:
#     print('invalid model')


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    adddatas = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    searching_talent = db.Column(db.Boolean, default=False)
    searching_description = db.Column(db.String(), nullable=True)
    future_shows = db.Column(db.PickleType, nullable=True)
    previous_shows = db.Column(db.PickleType, nullable=True)
    previous_shows_count = db.Column(db.Integer, default=0, nullable=True)
    future_shows_count = db.Column(db.Integer,default=0, nullable=True)
    
    def __repr__(self) -> str:
        return f'id:{self.id} name:{self.name} city: {self.city}'

    # : implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_venues = db.Column(db.Boolean, default=False)
    searching_description = db.Column(db.String(), nullable=True)
    future_shows = db.Column(db.PickleType, nullable=True, default=[])
    previous_shows = db.Column(db.PickleType, nullable=True, default=[])
    previous_shows_count = db.Column(db.Integer, default=0, nullable=True)
    future_shows_count = db.Column(db.Integer,default=0, nullable=True)

    def __repr__(self) -> str:
        return f'id:{self.id} name:{self.name} city: {self.city}'

    # : implement any missing fields, as a database migration using Flask-Migrate

#  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.String())

    def updateRecords(self,Artist,Venue):

      artist = Artist.query.get(self.artist_id)
      venue = Venue.query.get(self.venue_id)
     
      if artist != null and venue != null:
        vrecordArtist = {
        "artist_id": self.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": self.start_time
        }

        arecordVenue = {
        "venue_id": self.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": self.start_time
        }

        date = format_datetime(self.start_time)
        dateArray = date.split(',')
        year = dateArray[-1][:5]
    
        if int(year) < int(datetime.today().year):
          try:
            adata = list(artist.previous_shows)
            vdata = list(venue.previous_shows)
            adata.append(arecordVenue)
            vdata.append(vrecordArtist)
            currentCount = int(artist.previous_shows_count) + 1
            vcurrentCount = int(venue.previous_shows_count) + 1
            artist.previous_shows = adata
            artist.previous_shows_count = currentCount
            venue.previous_shows = vdata
            venue.previous_shows_count = vcurrentCount
            db.session.commit()
            print('committed')
            print(db.query.all())
          except:
            print(sys.exc_info)
          finally:
            print('ended')

        elif int(year) > int(datetime.today().year):
          try:
            adata = list(artist.future_shows)
            adata.append(arecordVenue)
            currentCount = int(artist.future_shows_count) + 1
            artist.future_shows = adata
            artist.future_shows_count = currentCount
            vdata = list(venue.future_shows)
            vdata.append(vrecordArtist)
            vcurrentCount = int(venue.future_shows_count) + 1
            venue.future_shows = vdata
            venue.future_shows_count = vcurrentCount
            
          except:
            print('there was an error--> ')
          finally:
            print('ended')
        else:
          try:
            adata = list(artist.future_shows)
            adata.append(arecordVenue)
            currentCount = int(artist.future_shows_count) + 1
            artist.future_shows = adata
            artist.future_shows_count = currentCount
            vdata = list(venue.future_shows)
            vdata.append(vrecordArtist)
            vcurrentCount = int(venue.future_shows_count) + 1
            venue.future_shows = vdata
            venue.future_shows_count = vcurrentCount
          
          except:
            print('there was an error--> ')
          finally:
            print('ended')

        
      else:
        return 'invalid ids'

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
  # : replace with real venues data.
  #       num_future_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_future_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_future_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_future_shows": 0,
    }]
  }]

  new_datas = Venue.query.all()
  new_datas_list = []

  for i in new_datas:
    new_datas_list.append({
      "city": i.city,
      "state":i.state,
      "venues":[{
        "id":i.id,
        "name":i.name,
        "num_future_shows":i.future_shows_count
      }]
    })

  return render_template('pages/venues.html', areas=new_datas_list);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  dataponse={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_future_shows": 0,
    }]
  }
  item = request.form.get('search_term', '')
  venues = []
  # venues.append(Venue.query.filter(Venue.name==f'{item}').first())
  venues.append(Venue.query.filter(Venue.name.ilike(f'%{item}')).first())
  venues.append(Venue.query.filter(Venue.name.ilike(f'%{item}%')).first())
  venues.append(Venue.query.filter(Venue.name.ilike(f'{item}%')).first())
  # venues.append(Venue.query.filter(Venue.city == item).first())
  # venues.append(Venue.query.filter(Venue.state =='NY').first())

  for i in venues:
    if i== None:
      venues.remove(i)

  venues_dataponse={
    "count":len(venues),
    "data": venues
  }
  print('-----')
  print(venues_dataponse['data'][0])

  return render_template('pages/search_venues.html', datas=venues_dataponse, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # : replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "adddatas": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "searching_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "previous_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "future_shows": [],
    "previous_shows_count": 1,
    "future_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "adddatas": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "previous_shows": [],
    "future_shows": [],
    "previous_shows_count": 0,
    "future_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "adddatas": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "previous_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "future_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "previous_shows_count": 1,
    "future_shows_count": 1,
  }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  new_datas = Venue.query.get(venue_id)
  if new_datas.genres[0] == '{':
      new_datas.genres = new_datas.genres.split('{')[1].split('}')[0].split(',')


  print(new_datas.genres)
  return render_template('pages/show_venue.html', venue=new_datas)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # : insert form data as a new Venue record in the db, instead

  name = request.form.get('name','')
  city = request.form.get('city','')
  state = request.form.get('state','')
  adddatas = request.form.get('adddatas','')
  phone = request.form.get('phone','')
  genres = request.form.get('genres','')
  facebook_link = request.form.get('facebook_link','')
  image_link = request.form.get('image_link','')
  website_link = request.form.get('website_link','')
  if request.form.get('searching_talent','') == '':
    searching_talent = False
  else:
    searching_talent = True
  searching_description = request.form.get('searching_description','')
  future_shows = request.form.get('future_shows',[])
  previous_shows = request.form.get('previous_shows',[])
  previous_shows_count = request.form.get('previous_shows_count',0)
  future_shows_count = request.form.get('future_shows_count',0)
  
  new_venue = Venue(name=name,city=city,state=state,adddatas=adddatas,phone=phone,genres=genres,facebook_link=facebook_link,
  image_link=image_link,searching_talent=searching_talent,searching_description=searching_description,future_shows=future_shows,
  previous_shows=previous_shows,previous_shows_count=previous_shows_count, website_link=website_link,future_shows_count=future_shows_count)

  # : modify data to be the data object returned from db insertion

  try:
    db.session.add(new_venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print('\n-------------\n')
    print(sys.exc_info())
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/hola', methods=['POST'])
def hola():
  a = request.form['hola']
  return a

@app.route('/venue/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # delete_venue('venue',venue_id)
  venue = Venue.query.get(venue_id)
  print('received')

  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    db.session.delete(venue)
    flash(f'Venue with {venue_id} was deleted successfully!')
    db.session.commit()
  except:
    print(sys.exc_info())
    flash(f'Error occurred while deleting Venue with {venue_id}!')
    print('\n=============')
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  General Search
#  --------------------------------------------------------------
@app.route('/region')
def region():

  new_datas = []

  return render_template('pages/artists.html', artists=new_datas)



@app.route('/region/search', methods=['POST'])
def region_search():
  datas = []
  data = []
  item = request.form.get('search_term', '')
  print('come on')
  datas.append(Artist.query.filter(Artist.city.ilike(f'%{item}%')).all())
  datas.append(Venue.query.filter(Venue.city.ilike(f'%{item}%')).all())
  print(datas)

  for i in datas:
    for a in i:
      data.append(a)
  print(data)


  dataponse = {
      "artist": False,
      "count": len(data),
      "data":data
  }

  print(datas)

  return render_template('pages/search_artists.html', datas=dataponse, search_term=request.form.get('search_term', ''))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # : replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  new_datas = Artist.query.all()

  return render_template('pages/artists.html', artists=new_datas)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  dataponse={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_future_shows": 0,
    }]
  }
  artists = []
  item = request.form.get('search_term', '')
  artists.append(Artist.query.filter(Artist.name.ilike(f'%{item}')).first())
  artists.append(Artist.query.filter(Artist.name.ilike(f'%{item}%')).first())
  artists.append(Artist.query.filter(Artist.name.ilike(f'{item}%')).first())

  for i in artists:
    if i== None:
      artists.remove(i)

  artist_dataponse = {
      "artist": True,
      "count": len(artists),
      "data":artists
  }

  print(artists)


  return render_template('pages/search_artists.html', datas=artist_dataponse, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # : replace with real artist data from the artist table, using artist_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "searching_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "previous_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "future_shows": [],
    "previous_shows_count": 1,
    "future_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "previous_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "future_shows": [],
    "previous_shows_count": 1,
    "future_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "previous_shows": [],
    "future_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "previous_shows_count": 0,
    "future_shows_count": 3,
  }
  new_datas = Artist.query.get(artist_id)
  if new_datas.genres[0] == '{':
    new_datas.genres = new_datas.genres.split('{')[1].split('}')[0].split(',')
  else:
    new_datas.genres=new_datas.genres.split(',')


  return render_template('pages/show_artist.html', artist=new_datas)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  new_artist = Venue.query.get(artist_id)
  form = ArtistForm(obj=new_artist)
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "searching_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # : populate form with fields from artist with ID <artist_id>
  new_artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=new_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # : take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name','')
  artist.city = request.form.get('city','')
  artist.state = request.form.get('state','')
  artist.phone = request.form.get('phone','')
  artist.genres = request.form.get('genres','')
  artist.facebook_link = request.form.get('facebook_link','')
  artist.image_link = request.form.get('image_link','')
  artist.website_link = request.form.get('website_link','')
  if request.form.get('looking_for_venues','') == '':
    artist.looking_for_venues = False
  else:
    artist.looking_for_venues = True
  artist.searching_description = request.form.get('searching_description','')


  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print('---------\n')
    print(sys.exc_info())
    flash('Artist ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()



  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  new_venue = Venue.query.get(venue_id)
  form = VenueForm(obj=new_venue)
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "adddatas": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "searching_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # : populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=new_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # : take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name','')
  venue.city = request.form.get('city','')
  venue.state = request.form.get('state','')
  venue.phone = request.form.get('phone','')
  venue.adddatas = request.form.get('adddatas','')
  venue.genres = request.form.get('genres','')
  venue.facebook_link = request.form.get('facebook_link','')
  venue.image_link = request.form.get('image_link','')
  venue.website_link = request.form.get('website_link','')
  if request.form.get('looking_for_venues','') == '':
    venue.searching_talent = False
  else:
    venue.searching_talent = True
  venue.searching_description = request.form.get('searching_description','')


  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print('---------\n')
    print(sys.exc_info())
    flash('Venue ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()

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
  name = request.form.get('name','')
  city = request.form.get('city','')
  state = request.form.get('state','')
  phone = request.form.get('phone','')
  genres = request.form.get('genres','')
  facebook_link = request.form.get('facebook_link','')
  image_link = request.form.get('image_link','')
  website_link = request.form.get('website_link','')
  if request.form.get('looking_for_venues','') == '':
    looking_for_venues = False
  else:
    looking_for_venues = True
  searching_description = request.form.get('searching_description','')
  future_shows = request.form.get('future_shows',[])
  previous_shows = request.form.get('previous_shows',[])
  previous_shows_count = request.form.get('previous_shows_count',0)
  future_shows_count = request.form.get('future_shows_count',0)
  
  new_artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,
  image_link=image_link,looking_for_venues=looking_for_venues,searching_description=searching_description,future_shows=future_shows,
  previous_shows=previous_shows,previous_shows_count=previous_shows_count, website_link=website_link,future_shows_count=future_shows_count)

  # : modify data to be the data object returned from db insertion

  try:
    db.session.add(new_artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print('\n-------------\n')
    print(sys.exc_info())
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # : replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]

  shows = Show.query.all()
  data = []

  for i in shows:
    artist = Artist.query.get(i.artist_id)
    venue = Venue.query.get(i.venue_id)
    data.append({
    "venue_id": i.venue_id,
    "venue_name": venue.name,
    "artist_id": i.artist_id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": i.start_time
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
  # : insert form data as a new Show record in the db, instead

  artist_id = request.form.get('artist_id','')
  venue_id = request.form.get('venue_id','')
  start_time = request.form.get('start_time')
  print('ssssss===>\n')
  print(start_time)

  show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)

  try:
    db.session.add(show)
    show.updateRecords(Artist,Venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
