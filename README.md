"# Edumy" 
# Model structure

Course Detail
=============
title
author
price
discount
duration
Full lifetime access
Assignments
Certificate of Completion
preview
overview
description
what will learn
requirements
Skill level
Language
best_seller
rating
tags
comments
enrolled
allowed memberships (manytomanyfield with Membership)
updated
timestamp



Membership 
==========
slug 
type (free, pro, enterprise) 
price (monthly) 
stripe plan id

UserMembership 
==============
user (foreignkey to default User) 
stripe customer id 
membership type (foreignkey to Membership)

Subscription 
============
user membership (foreignkey to UserMembership) 
stripe subscription id 
active


Chapter
=======
title
course


Lesson
======
title
position
duration
chapter
video
thumbnail



Instructor
==========
name
title
avatar
overview
eductaion
phone
email
skype
facebook
twitter
instagram
linkedin
instagram
Experience
timestamp
created
active



Event
=====
title
subtitle
image
date
time
address
phone
email
site
tgas
description
content
Participants -> User
comments
created at


Blog
====
title
description
content
comments
author
image
category
tags
