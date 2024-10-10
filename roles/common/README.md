Role Variables
--------------

For check\_openstack\_services\_rhoso.yml tasks:
   common\_verify\_resources\_are\_ready
      - List of dicts of resources to check if they're ready
        Each dict should include the following keys: kind, name, condition\_type 
        Example:
           kind: metricstorage
           name: metric-storage
           condition_type: Ready
