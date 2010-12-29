# -*- coding: utf-8 -*-

import unittest

import gpxpy.gpx as _gpx
import gpxpy.parser as _parser
import time as _time

class TestWaypoint( unittest.TestCase ):

	def _parse( self, file ):
		f = open( 'test_files/%s' % file )
		parser = _parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		if not gpx:
			print 'Parser error: %s' % parser.get_error()

		return gpx
		
	def _reparse( self, gpx ):
		xml = gpx.to_xml()

		parser = _parser.GPXParser( xml )
		gpx = parser.parse()

		if not gpx:
			print 'Parser error while reparsing: %s' % parser.get_error()

		return gpx

	def test_waypoints_equality_after_reparse( self ):
		gpx = self._parse( 'cerknicko-jezero.gpx' )
		gpx2 = self._reparse( gpx )

		self.assertTrue( gpx.waypoints == gpx2.waypoints )
		self.assertTrue( gpx.routes == gpx2.routes )
		self.assertTrue( gpx.tracks == gpx2.tracks )
		self.assertTrue( gpx == gpx2 )

	def test_has_times_false( self ):
		gpx = self._parse( 'cerknicko-without-times.gpx' )
		self.assertFalse( gpx.has_times() )

	def test_has_times( self ):
		gpx = self._parse( 'korita-zbevnica.gpx' )
		self.assertTrue( len( gpx.tracks ) == 4 )
		# Empty -- True
		self.assertTrue( gpx.tracks[ 0 ].has_times() )
		# Not times ...
		self.assertTrue( not gpx.tracks[ 1 ].has_times() )

		# Times OK
		self.assertTrue( gpx.tracks[ 2 ].has_times() )
		self.assertTrue( gpx.tracks[ 3 ].has_times() )

	def test_unicode( self ):
		gpx = self._parse( 'unicode.gpx' )

		name = gpx.waypoints[ 0 ].name

		self.assertTrue( name.encode( 'utf-8' ) == 'šđčćž' )

	def test_nearest_location_1( self ):
		gpx = self._parse( 'korita-zbevnica.gpx' )

		location = _gpx.Location( 45.451058791, 14.027903696 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( location ) < 0.001 )
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = _gpx.Location( 1, 1 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = _gpx.Location( 50, 50 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

	def test_long_timestamps( self ):
		# Check if timestamps in format: 1901-12-13T20:45:52.2073437Z work
		gpx = self._parse( 'Mojstrovka.gpx' )

		# %Y-%m-%dT%H:%M:%SZ'

	def test_reduce_gpx_file( self ):
		f = open( 'test_files/Mojstrovka.gpx' )
		parser = _parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		max_reduced_points_no = 200

		started = _time.time()
		gpx = parser.parse()
		points_original = len( gpx.get_points() )
		time_original = _time.time() - started

		gpx.reduce_points( max_reduced_points_no )

		points_reduced = len( gpx.get_points() )

		result = gpx.to_xml()
		result = result.encode( 'utf-8' )

		started = _time.time()
		parser = _parser.GPXParser( result )
		parser.parse()
		time_reduced = _time.time() - started

		print time_original
		print points_original

		print time_reduced
		print points_reduced

		self.assertTrue( time_reduced < time_original )
		self.assertTrue( points_reduced < points_original )
		self.assertTrue( points_reduced < max_reduced_points_no )

if __name__ == '__main__':
	unittest.main()
