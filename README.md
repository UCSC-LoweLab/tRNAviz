

## Django apps

- Django REST Framework: used to render JSON
- django-debug-toolbar
- import-export: for admin console and GUI imports, but also provides shell handles for db


## Main pages

tRNAviz is organized into two main apps, **explorer** and **comparer**. The **Explorer** provides visualizations for tRNAs processed by my pipeline. The **Summary** page is a dashboard that details consensus elements and summary statistics for a clade and isotype. The **Tilemap** page shows more information about the specific clade and provides summary statistics.

The **Comparer** takes several selections and compares them to a reference selection. Selections can correspond to individual tRNAs or groups of tRNAs, including user uploaded sequences.


