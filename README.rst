Feature-verification-tests are made up of two parts: tests and callback plugins.

The callback plugins output the test results in different ways.
The custom_logger plugin takes a test-id from the task names and reports the results of the tests in a file, where each line contains a test ID and a result (pass/fail).
The custom_junit plugin extends the standard ansible junit plugin and report in XML format that Polarion expects.


The tests are STF and for telemetry services in RHOSO.

STF tests
These are the functional tests for stf. They check that OpenStack components are running and connected to STF and that the system works end-to-end.
They are based on an infrared depoyment.

RHOSO telemetry tests
These tests cover telemetry features in RHOSO-18. These tests check that the telemetry-operator has deployed and configured the required services as expected.


