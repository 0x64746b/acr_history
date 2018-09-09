#!/usr/bin/env python3
# coding: utf-8


import requests
import sys
import time

import sqlalchemy.ext.declarative
import sqlalchemy.orm

engine = sqlalchemy.create_engine('sqlite:///acr_history.db')
Session = sqlalchemy.orm.sessionmaker(bind=engine)

Base = sqlalchemy.ext.declarative.declarative_base()


class PlaylistEntry(Base):
    __tablename__ = 'playlist'

    timestamp = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    artist = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return ', '.join([str(self.timestamp), self.artist, self.title])


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session()

    last_time = int(time.time())

    try:
        while True:
            response = requests.post(
                'https://absoluteradio.co.uk/_ajax/recently-played.php',
                data={
                    'lastTime': last_time,
                    'serviceID': 12,
                    'searchTerm': '',
                    'mode': 'more'}
                )

            try:
                response.raise_for_status()
            except requests.RequestException:
                sys.stdout.write('|x|')
                continue

            songs = response.json()['events']
            for song in songs:
                session.add(PlaylistEntry(
                    timestamp=song['EventTimestamp'],
                    artist=song['ArtistName'].strip(),
                    title=song['AllTrackTitle'].strip(),
                ))
                try:
                    session.commit()
                except sqlalchemy.exc.IntegrityError:
                    session.rollback()
                    sys.stdout.write('-')
                else:
                    sys.stdout.write('.')
                finally:
                    last_time = song['EventTimestamp'] - 1
                    sys.stdout.flush()
    except KeyboardInterrupt:
            session.close()
