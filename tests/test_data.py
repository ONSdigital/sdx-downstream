survey_ce_census = '''
{
  "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
  "type": "uk.gov.ons.edc.eq:surveyresponse",
  "version": "0.0.1",
  "origin": "uk.gov.ons.edc.eq",
  "survey_id": "0",
  "collection": {
    "exercise_sid": "hfjdskf",
    "instrument_id": "ce2016",
    "period": "0616"
  },
  "submitted_at": "2016-03-12T10:39:40Z",
  "metadata": {
    "user_id": "789473423",
    "ru_ref": "1234570071A"
  },
  "data": {
    "1": "2",
    "2": "4",
    "3": "2",
    "4": "Y"
  }
}
'''

survey_hh_census = '''
{
  "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
  "metadata": {
    "ru_ref": "12346789012A",
    "user_id": "davidjones"
  },
  "submitted_at": "2016-07-14T15:42:25Z",
  "origin": "uk.gov.ons.edc.eq",
  "survey_id": "0",
  "collection": {
    "instrument_id": "hh2016",
    "exercise_sid": "502",
    "period": "201605"
  },
  "data": {
    "agegroup": "1",
    "whypaper": ["2", "5", ""],
    "visit": "Y",
    "help1": "3",
    "howcomplete": "1",
    "device": ["1", "2", "3", "5", ""],
    "deviceother": "Facebook",
    "helpother": "Warren helped me",
    "help2": ["1", "3", ""],
    "paperother": "My computer is broken",
    "help2other": "Smoke Signals",
    "find": "Y"
  },
  "version": "0.0.1",
  "type": "uk.gov.ons.edc.eq:surveyresponse"
}
'''

survey_with_tx_id = '''
{
  "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
  "type": "uk.gov.ons.edc.eq:surveyresponse",
  "version": "0.0.1",
  "origin": "uk.gov.ons.edc.eq",
  "survey_id": "023",
  "collection": {
    "exercise_sid": "hfjdskf",
    "instrument_id": "0102",
    "period": "1604"
  },
  "submitted_at": "2016-03-12T13:01:26Z",
  "metadata": {
    "user_id": "789473423",
    "ru_ref": "12345678901A"
  },
  "data": {
    "11": "1/4/2016",
    "12": "31/10/2016",
    "20": "1800000",
    "21": "60000"
  }
}
'''
