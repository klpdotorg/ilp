Changelog
---
Release 1.3.0: db9840a07ee1b7f1bb64163289e1c6f15088fd74 2019-02-01
  - OTP validate and reset password reset endpoints now return the full user object. This helps to improve Konnect signup and login UX.
  - GKA dashboard
    - URL change for school filters
  - Removed GP contest dashboard link
  - Project 1 million
    - Analytics portal
  - Data updates
    - Institution tag mapping

Release 1.2.1: 5a60cd87bf3d2984afbe36c387cdbab8ae05c0e5 2019-01-15
	- Project 1 million updates
	- Updated Django version to 1.11.8
	- Included Gujarat and Andhra Pradesh in states endpoint	

Release xxxx: December 19,2018
	- Fixed permissions issue with students endpoint. Made it more secure

Release xxxx: Nov. 23, 2018
	- Modified 1 million reports code to read gp_code instead of gp_name
	- Fixed bug related to multiple qgroups mapped to a gp or school
	- Reports will now be generated even if community survey data is not present for a boundary.

Release 1.2.0: fc90e8c459b9d9ba621b08f318ed4c34284e1cea 2018-11-18
  - Karnataka GKA dashboard
    - Removed "Assessment" section
    - Bug fixes and improvements
  - ILP Konnect
    - Resent OTP feature
    - Improved crash analytics
    - Ability to sync large amounts of assessment data
    - Dropped support for Android version <= 4
  - Odisha GKA dashboard
    - Enabled GP contest section
    - Added new Survey, QuestionGroups etc.
    - Loaded the GP Contest data.
  - GP contest data
    - Bug fixes (Fixed the 21,22,23 answer issue for current academic year)
    - New logic for calcuating correct answer for competencies
    - New questions for current academic year
  - Project 1 million
    - Uses aggregates to query data and thereby runs faster
    - Supports sending only one section of a report or a combination of sections
    - Added new competency evaluations 
    - Refactored templates to use inheritance
    - Fixed issues with generating reports when GKA data for a child boundary was not present
    - Added an overall gradewise performance summary for districts/blocks/clusters and gram panchayats
    - Modified footer verbiage per direction from program/research/field and KLP team leads.
    - Fixed alignment issues with Kannada reports
    - Bug fix: fixed # of Gp contests number to show proper count
  - ILP Superset
    - Fetches data directly from ILP DB to show current data
    - Upgraded superset version


Release 1.1.5: 2018-10-21
  - Corrected the logic for gender correct answer calculation 
  - Corrected the spelling mistakes of gender in GP Contest assessments
  - GKA Dashboard updates
      - Changed the text for Odisha GKA Dashboard
      - Removed respondent graph from "Surveys section"

Release 1.1.4: 7245329b5d57c6d424fa0cfe23de1daf6a211dba 2018-10-12
  - Removed respondent section in GKA dashboard's "Survey" section
  - Upgraded django in production for 1.11.5 security fix
  - SQL updates for Odisha data

Release 1.1.3: ac5c630dc5ced82c9466196e839fa66b64b6600e - 2018-10-11
  - GKA dashboard bug fixes
  - Management command for bringing live data to superset sqlite db
  - Endpoint fixes related to survey tags
  - SQL updates
    - GP contest import
    - Teacher survey deactivation
  - Odisha script updates
