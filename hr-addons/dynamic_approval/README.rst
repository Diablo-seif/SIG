
.. class:: text-center

Dynamic Approval
================

.. class:: text-left

Features
--------

- Add relation between approval category and any other module

.. class:: text-left

Usage
-----

#. Open **Approvals** application
#. From **Configuration** menu select **Approvals Types**
#. Press create then type a name, then choose **Model Approval**
#. Select **Action** and construct a domain to perform when run the action

.. class:: text-left

How It Work
-----------

#. on installing this module **x_approval_category_id** field will be created for all models in the system
#. When you create new approval request with model and action type
#. **NEW REQUEST** button will return action in form mode and context `{'default_x_approval_category_id': approval_category.id}`
#. **TO REVIEW** button will return action in tree mode and will filter the record set using the selected domain

.. class:: text-left

Credits
-------

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Muhamed Abd El-Rhman <muhamed.abdelrhman@core-bpo.com>`_ |copy|
  `CORE B.P.O <http://www.core-bpo.com>`_ |tm| 2020
