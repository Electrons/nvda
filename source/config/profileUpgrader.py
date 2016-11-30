# -*- coding: UTF-8 -*-
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2016 NV Access Limited
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

from logHandler import log
from configSpec import latestSchemaVersion, confspec
from configobj import flatten_errors
from copy import deepcopy
import profileUpgradeSteps

schemaVersionKey = "schemaVersion"

def upgrade(profile, validator):
	# when profile is none or empty we can still validate. It should at least have a version set.
	log.info("Checking schema version of config:\n%s" % profile)
	_ensureVersionProperty(profile)
	startSchemaVersion = int(profile[schemaVersionKey])
	log.info("Current config schema version: {0}, latest: {1}".format(startSchemaVersion, latestSchemaVersion))

	for fromVersion in xrange(startSchemaVersion, latestSchemaVersion):
		_doConfigUpgrade(profile, fromVersion)
	_doValidation(deepcopy(profile), validator) # copy the profile, since validating mutates the object
	profile.write()

def _doConfigUpgrade(profile, fromVersion):
	toVersion = fromVersion+1
	upgradeStepName = "upgradeConfigFrom_{0}_to_{1}".format(fromVersion, toVersion)
	upgradeStepFunc = getattr(profileUpgradeSteps, upgradeStepName)
	log.info("Upgrading from schema version {0} to {1}".format(fromVersion, toVersion))
	upgradeStepFunc(profile)
	profile[schemaVersionKey] = toVersion

def _doValidation(profile, validator):
	oldConfSpec = profile.configspec
	profile.configspec = confspec
	result = profile.validate(validator, preserve_errors=True)
	profile.confspec = oldConfSpec

	if isinstance(result, bool) and not result:
		# empty file?
		raise ValueError("Unable to validate config file after upgrade.")

	flatResult = flatten_errors(profile, result)
	for section_list, key, value in flatResult :
		 # bool values don't matter
		 #	True and the value is fine.
		 #	False and the value is missing (which is typically fine)
		 # dict values should be recursively checked 
		if not isinstance(value, bool):
			errorString=(
				"Unable to validate config file after upgrade: Key {0} : {1}\n" +
				"Full result: (value of false means the key was not present)\n" +
				"{2}"
				).format(key, value, flatResult)
			raise ValueError(errorString)

def _ensureVersionProperty(profile):
	isEmptyProfile = 1 > len(profile.keys())
	if isEmptyProfile:
		log.info("Empty profile, triggering default schema version")
		profile[schemaVersionKey] = latestSchemaVersion
	elif not schemaVersionKey in profile:
		# this must be a "before schema versions" config file.
		log.info("No schema version found, setting to zero.")
		profile[schemaVersionKey] = 0