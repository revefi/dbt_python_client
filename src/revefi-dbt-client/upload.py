from revefi_dbt_client.main import main

"""This python module only exists for legacy reasons.

When the the dbt python client was first introduced, it was a single file with hyphen in the package name.

As per PEP8, hyphens are not allowed in package names, so in the later versions the package name was changed to use
underscores.

However, this module is still in-use by the customers, thus it cannot be deleted immediately.
Once all the customers migrate to the new package name, this module can be removed.  
"""

if __name__ == "__main__":
    main()
