===========
Concepts
===========

Users
======

Obviously Minddrag has the concept of registered users. Users are required to
have a unique username, a password and a valid email address. The user can
choose to provide more information in her profile and decide who may view it.
Registration is done via the common double opt-in mechanism; using an activation
through a link sent to the users email address.

Teams
======

Users can create teams and invite other users to join them. Teams can either be
public or private. A team is used to work on a specific topic and collect all
the data from all team members in one place.

Maybe some kind of namespace mechanism should be implemented, at least for
private teams. This is to prevent the case that user A cannot create a private
team called "SuperSecretResearch" because user B has already created one for
himself.

Dragables
==========

***FIXME*** elaborate

A dragable is a piece of information on the web. 

Dragables are identified by a unique hash value. Furthermore, every dragable
belongs to a team, is located at a URL and stores when and by whom it was
created and when it was last modified. A Dragable can be connected to another
dragable. This is used to span multiple content types within an HTML page, such
as some text, a hyperlink and then some more text. This would be stored as three
connected dragables.

Annotations
============

Dragables can be annotated by the user. Various types of content can be used for
annotations. All annotations have in common that they are associated to the
dragable that they annotate, are identified by a unique hash and store when and
by whom they were created and when they were last modified.

Text Annotation
----------------

The simplest kind of annotation is a textual note, written by the user.

Link Annotation
----------------

Dragables can be annotated with URLs that point to some information which is
relevant to the annotated dragable. In addition to the URL, a link annotation
can have an optional textual description.

Image Annotation
----------------

An image annotation is a special kind of link annotation that points to an
image. Like a link annotation, an image annotation can have an optional textual
description.

Video Annotation
----------------

A video annotation is a special kind of link annotation that points to a
video. Like a link annotation, a video annotation can have an optional textual
description.

Additionally, a "type" field is provided. The type of a video annotation could
be something like "youtube" or "vimeo". Knowing this information about a video
annotation might enable automatic embedding, if the video is hosted on a site
for which the embedding URL scheme is known.

File Annotation
----------------

File annotations are different to the other kinds of annotations in that they do
not point to information elsewhere on the web. Instead, they represent a file
that was uploaded by the user who created the annotation. File annotations can
have optional textual description.

Connection Annotation
---------------------

A connection annotation is a special kind of annotation that connects two
dragables. The mindmap structure which the user manipulates when working with
Minddrag is made up of Dragables that are connected by connection annotations.

