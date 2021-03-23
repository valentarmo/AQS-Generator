import unittest
import pycountry
import DataGenerator

class DataGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        countries = list(pycountry.countries)
        country_codes = list(map(lambda country: country.alpha_2, countries))
        DataGeneratorTest.country_codes = country_codes
        DataGeneratorTest.data = DataGenerator.generate_data(country_codes)


    def test_generated_data_keys(self):
        required_keys = [
            'location', 
            'value',
            'unit',
            'particle',
            'country_code',
            'entity_name1',
            'entity_name2',
            'date_utc',
            'date_local',
            'entity',
            'some_boolean',
            'latitude',
            'longitude',
            'interval',
            'time_unit'
        ]
        self.assertCountEqual(list(DataGeneratorTest.data.keys()), required_keys)
    
    def test_generated_data_value_types(self):
        data = DataGeneratorTest.data
        self.assertIs(type(data['location']), type(''))
        self.assertIs(type(data['value']), type(0.0))
        self.assertIs(type(data['unit']), type(''))
        self.assertIs(type(data['particle']), type(''))
        self.assertIs(type(data['country_code']), type(''))
        self.assertIs(type(data['entity_name1']), type(''))
        self.assertIs(type(data['entity_name2']), type(''))
        self.assertIs(type(data['date_utc']), type(''))
        self.assertIs(type(data['date_local']), type(''))
        self.assertIs(type(data['entity']), type(''))
        self.assertIs(type(data['some_boolean']), type(True))
        self.assertIs(type(data['latitude']), type(0.0))
        self.assertIs(type(data['longitude']), type(0.0))
        self.assertIs(type(data['interval']), type(1))
        self.assertIs(type(data['time_unit']), type(''))

    def test_generated_data_values(self):
        data = DataGeneratorTest.data
        self.assertGreaterEqual(data['value'], 0)
        self.assertGreaterEqual(data['latitude'], -90)
        self.assertGreaterEqual(data['longitude'], -180)
        self.assertLessEqual(data['value'], 100)
        self.assertLessEqual(data['latitude'], 90)
        self.assertLessEqual(data['value'], 180)
        self.assertIn(data['particle'], ['pm10', 'pm25', 'so2', 'so3', 'co', 'no2'])
        self.assertIn(data['time_unit'], ['hours', 'minutes', 'seconds', 'days'])
        self.assertIn(data['unit'], ['µg/m³'])
        self.assertIn(data['country_code'], DataGeneratorTest.country_codes)

if __name__ == '__main__':
    unittest.main()