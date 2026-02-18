.. class:: text-left

Egyptian Deduction Taxes
========================

Egyptian Deduction Taxes Localization

Usage
=====

* Add some fields in partner to add deduction tax details
* Add deduction/withholding taxes and tax groups as data
* Add fields to can configure deduction/withholding taxes on products
  - Go to: products form
  - you can configure taxes under General Information Tab
  - Choose Deduction Tax and Withholding Tax
* you can Define Account Journal with type `cash` and enable taxation on it
  to separate this journal from other cash journals
* Calculate Deduction Taxes on Invoices
* Each invoice has a grouped table by deduction tax which includes
  Tax Amount depends on Deduction Tax
* to register deduction:
  - go to vendor bill
  - press register deduct
  - choose journal of deduction that you created later
  - choose Deduction Payment Type : full or percentage and set the percent
  -  the deduction amount will be calculated, validate it
* to register deduction for bulk payments:
  - go to vendor bill list.
  - select your bills.
  - from actions menu, press register deduction tax.
  - if deduction type journal, is not defined, error message, will be displayed.	
  - if there is an invoice not matched the payment criteria, error message, will be displayed.	
  - choose journal of deduction that you created later.
  - Deduction Payment Type will be full by default.
  - press create payment button.
  - the deduction amount will be calculated, validate it.

* New Button to View Payments from Invoices/Bills
* Generate Deduction Tax Report
  - in Invoicing go to Reporting > Deduction Tax Report
  - you can view all deduction lines and all its details
  -you can use filter and search on lines based on Duration, Year And Vendor


Credits
-------

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Islam Abdelmaaboud <eslam.abdelmabood@core-bpo.com>`_ |copy|
  `CORE B.P.O <http://www.core-bpo.com>`_ |tm| 2019
