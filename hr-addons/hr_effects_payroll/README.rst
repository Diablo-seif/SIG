.. class:: text-left

HR Effects Payroll
==================

This is Core Effects Payroll Module that you can create Deductions and Additions Type and values


Features
--------

#. Create Deductions Category
#. Create Additions Type
#. Create Deductions Types and Value
#. Create Additions Types and Value


Salary Rule
-----------

1. Effects Payroll Additions python call code:
   result = employee.get_effects_payroll('additions', payslip.date_from, payslip.date_to, code=False)


2. Effects Payroll Deductions python call code:
   result = employee.get_effects_payroll('deductions', payslip.date_from, payslip.date_to, code=False)


.. class:: text-left

Credits
-------

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Hashem Aly <hashem.aly@core-bpo.com>`_ |copy|
  `CORE B.P.O <http://www.core-bpo.com>`_ |tm| 2020
