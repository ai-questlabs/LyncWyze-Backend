---
config:
  layout: elk
---
erDiagram

  HOUSEHOLDS {
    uuid id
    text name
    text address
    text location
    datetime created_at
  }

  USERS {
    uuid id
    firebase_uid
    uuid household_id
    text email
    text first_name
    text last_name
    text phone
    text avatar_url
    boolean is_primary
    boolean verified
    datetime created_at
  }

  KIDS {
    uuid id
    uuid household_id
    uuid parent_user_id
    text first_name
    date dob
    text gender
    text avatar_url
    datetime created_at
  }

  VEHICLES {
    uuid id
    uuid household_id
    text make
    text model
    text color
    int seat_count
    datetime created_at
  }

  ACTIVITIES {
    uuid id
    uuid created_by_user_id
    text provider
    text name
    text address
    text location
    text recurrence_rule
    time start_time
    time end_time
    datetime created_at
  }

  KID_ACTIVITY_ENROLLMENTS {
    uuid id
    uuid kid_id
    uuid activity_id
    datetime enrolled_at
  }

  CARPOOLS {
    uuid id
    uuid activity_id
    uuid owner_user_id
    text name
    boolean open_to_outsiders
    boolean open_to_carpool
    int capacity
    datetime created_at
  }

  CARPOOL_MEMBERS {
    uuid id
    uuid carpool_id
    uuid user_id
    text role
    datetime joined_at
  }

  INVITATIONS {
    uuid id
    uuid carpool_id
    uuid inviter_user_id
    uuid invitee_user_id
    text invitee_email
    text invitee_phone
    text token
    text status
    datetime created_at
    datetime expires_at
  }

  ACTIVITY_INSTANCES {
    uuid id
    uuid activity_id
    datetime start_at
    datetime end_at
  }

  ASSIGNMENTS {
    uuid id
    uuid carpool_id
    uuid instance_id
    text leg
    uuid assigned_user_id
    uuid created_by_user_id
    datetime created_at
  }

  AVAILABILITY_SLOTS {
    uuid id
    uuid household_id
    int weekday
    time start_time
    time end_time
    uuid created_by_user_id
    datetime created_at
    datetime updated_at
  }

  NOTIFICATIONS {
    uuid id
    uuid user_id
    text type
    text payload
    boolean read
    datetime created_at
  }

  AUDITS {
    uuid id
    uuid user_id
    text entity
    uuid entity_id
    text action
    text metadata
    datetime created_at
  }

  GEOCODING_CACHE {
    uuid id
    text address
    text address_hash
    text location
    text provider
    datetime cached_at
  }

  VERIFICATIONS {
    uuid id
    uuid user_id
    text provider
    text status
    datetime created_at
  }

  HOUSEHOLDS ||--o{ USERS : has
  HOUSEHOLDS ||--o{ KIDS : has
  HOUSEHOLDS ||--o{ VEHICLES : has
  HOUSEHOLDS ||--o{ AVAILABILITY_SLOTS : has

  USERS ||--o{ KIDS : parent_of
  USERS ||--o{ ACTIVITIES : creates
  USERS ||--o{ CARPOOLS : owns
  USERS ||--o{ CARPOOL_MEMBERS : member
  USERS ||--o{ INVITATIONS : sent
  USERS ||--o{ ASSIGNMENTS : assigned_to
  USERS ||--o{ NOTIFICATIONS : receives
  USERS ||--o{ VERIFICATIONS : has

  KIDS ||--o{ KID_ACTIVITY_ENROLLMENTS : enrolled_in
  ACTIVITIES ||--o{ KID_ACTIVITY_ENROLLMENTS : has_enrollments
  ACTIVITIES ||--o{ ACTIVITY_INSTANCES : generates
  ACTIVITY_INSTANCES ||--o{ ASSIGNMENTS : schedule_for

  CARPOOLS ||--o{ CARPOOL_MEMBERS : has
  CARPOOLS ||--o{ INVITATIONS : invites
  CARPOOLS ||--o{ ASSIGNMENTS : assignments

  INVITATIONS }o--|| USERS : invitee
  INVITATIONS }o--|| USERS : inviter
  INVITATIONS }o--|| CARPOOLS : relates