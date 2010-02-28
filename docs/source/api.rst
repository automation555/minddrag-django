==================
RESTful HTTP API
==================

General Information
====================

TODO

URL
++++

versioned API

/api/1.0/

Formats
++++++++

default: json
also available: xml, yaml
(use ``format`` URL parameter)

Authentication
==============

TODO

API Methods
=============

Teams
++++++

Retrieve Teams
---------------

**URL**

/teams/**:name**/

**HTTP Method**

GET

**Searching**

Don't include ``name`` in the URL and use a parameter ``search`` instead.

**Access Restrictions**

Authentication is not required. Results will contain public and private teams.

**Example** ::

    curl -s http://localhost:8000/api/teams/ | jsonpretty
    [
      {
        "name": "The A-Team",
        "public": true,
        "created_by": {
          "username": "hannibal"
        },
        "members": [
          {
            "username": "hannibal"
          },
          {
            "username": "face"
          },
          {
            "username": "ba"
          },
          {
            "username": "murdock"
          }
        ],
        "description": "Don't you love it when a plan comes together?"
      },
      {
        "name": "testteam",
        "public": true,
        "created_by": {
          "username": "hs"
        },
        "members": [

        ],
        "description": ""
      }
    ]

Create Team
------------

**URL**

/teams/

**HTTP Method**

POST

**Parameters**

- *name*: Name of the team
- *description*: Description of the team (optional)
- *password*: Password required to join this team. (optional) If this Parameter is present and non-empty, the team will be private.

**Access Restrictions**

Authentication is required.

**Example**

TODO

Update Team
-------------

**URL**

/teams/**:name**/

**HTTP Method**

PUT

**Parameters**

One or more of the following:

- *name*: Name of the team
- *description*: Description of the team (optional)
- *public*: Boolean field (default true)
- *password*: Password required to join this team. Required if ``public`` is ``false``, ignored otherwise.

**Access Restrictions**

Authentication is required. The authenticated user must be the creator of the
team.

**Example**

TODO

Delete Team
------------

**URL**

/teams/**:name**/

**HTTP Method**

DELETE

**Access Restrictions**

Authentication is required. The authenticated user must be the creator of the
team.

**Example**

TODO

Dragables
++++++++++

Retrieve Dragables
-------------------

**URL**

/dragables/**:hash**/

``hash`` is optional. When given, only the dragable with this hash id is
returned.

**HTTP Method**

GET

**Parameters**

**Notice:** Don't include the ``hash`` in the URL when using these.

- *start*: Offset to start at (default 0)
- *limit*: Number of dragables returned (default 25, max 100)
- *team*: Retrieve all dragables that belong to this team.

**Searching**

Instead of ``team``, add a parameter ``search``.

**Access Restrictions**

- When retrieving an individual dragable:

	Authentication is only required if the dragable belongs to a private team.
	The authenticated user must be a member of the team.

- When retrieving all dragables for a given team:

	Authentication is only required if the team is private. The authenticated
	user must be a member of the team.

- When retrieving all dragables matching a given search term:

	Search results for authenticated requests include dragables from private
	teams that the authenticated user is a member of.

**Example**

TODO

Create Dragable
----------------

**URL**

/dragables/

**HTTP Method**

POST

**Parameters**

- *hash*: The unique hash that identifies this dragable.
- *team*: The team to which this dragable belongs.
- *url*: The URL that this dragable references.
- *xpath*: The XPath query that selects the content this dragable references.
- *title*: The title of this dragable. (optional)
- *text*: FIXME (optional)
- *conntected_to*: The unique hash of an existing dragable, to which this dragable is connected. (optional)

**Access Restrictions**

Authentication is required.

**Example**

TODO

Update Dragable
----------------

**URL**

/dragables/**:hash**/

**HTTP Method**

PUT

**Parameters**

One or more of the following

- *team*: The team to which this dragable belongs.
- *url*: The URL that this dragable references.
- *xpath*: The XPath query that selects the content this dragable references.
- *title*: The title of this dragable. (optional)
- *text*: FIXME (optional)
- *conntected_to*: The unique hash of an existing dragable, to which this dragable is connected.

**Access Restrictions**

Authentication is required. The authenticated user must be a member of the team
that the dragable belongs to.

**Example**

TODO

Delete Dragable
----------------

**URL**

/dragables/**:hash**/

**HTTP Method**

DELETE

**Access Restrictions**

Authentication is required. The authenticated user must be a member of the team
that the dragable belongs to.

**Example**

TODO

Annotations
++++++++++++

Retrieve Annotations
---------------------

**URL**

/annotations/**:hash**/

``hash`` is optional. When given, only the annotation with this hash id is
returned.

**HTTP Method**

GET

**Parameters**

**Notice:** Don't include the ``hash`` in the URL when using these.

- *start*: Offset to start at (default 0)
- *limit*: Number of dragables returned (default 25, max 100)
- *dragable*: Retrieve all annotations that belong to this dragable.

**Searching**

Instead `dragable``, add a parameter ``search``.

**Access Restrictions**

Anonymous requests only include annotations of dragables that belong to public
teams. Authenticated requests include data from private teams that the
authenticated user is a member of (analogous to API calls for dragables).

**Example**

TODO

Create Annotation
------------------

**URL**

/annotations/

**HTTP Method**

POST

**Parameters**

- *hash*: The unique hash that identifies this annotation.

- *dragable*: The unique hash of the dragable that is annotated.

- *type*: The type of the annotation, one of ``note``, ``url``, ``image``, ``video``, ``file``

- additional parameters for note annotations:
   * *text*: The content of the note annotation.

- additional parameters for URL annotations:
   * *url*: The content of the URL annotation.
   * *description*: A textual description of the annotation. (optional)

- additional parameters for image annotations:
   * *url*: The URL of the image that should be used to annotate the dragable.
   * *description*: A textual description of the annotation. (optional)
   
- additional parameters for video annotations:
   * *url*: The URL of the video that should be used to annotate the dragable.
   * *description*: A textual description of the annotation. (optional)
   * *type*: One of ``youtube``, ``vimeo``, ``viddler``, ``blip.tv``, etc. (optional)

- additional parameters for file annotations:
   * FIXME file upload OMG BBQ!!1!

**Access Restrictions**

Authentication is required.

**Example**

TODO

Update Annotation
------------------

**URL**

/annotations/**:hash**/

**HTTP Method**

PUT

**Parameters**

**Notice:** The type of an annotation can not be changed.

One or more of the following:

- *dragable*: The unique hash of the dragable that is annotated.

- parameters for note annotations:
   * *text*: The content of the note annotation.

- parameters for URL annotations:
   * *url*: The content of the URL annotation.
   * *description*: A textual description of the annotation.

- parameters for image annotations:
   * *url*: The URL of the image that should be used to annotate the dragable.
   * *description*: A textual description of the annotation.
   
- parameters for video annotations:
   * *url*: The URL of the video that should be used to annotate the dragable.
   * *description*: A textual description of the annotation. (optional)
   * *type*: One of ``youtube``, ``vimeo``, ``viddler``, ``blip.tv``, etc.

- parameters for file annotations:
   * FIXME file upload OMG BBQ!!1!

**Access Restrictions**

Authentication is required. The authenticated user must be a member of the team
to which the annotated dragable belongs.

**Example**

TODO

Delete Annotation
------------------

**URL**

/annotations/**:hash**/

**HTTP Method**

DELETE

**Access Restrictions**

Authentication is required. The authenticated user must be a member of the team
to which the annotated dragable belongs.

**Example**

TODO
