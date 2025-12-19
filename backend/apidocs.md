KidRide Backend API (OpenAPI excerpt)

Notes:
- Relative paths only; prepend your desired host (e.g., http://localhost:5000).
- Protected routes require `Authorization: Bearer <idToken>` where the token is a Firebase ID token.
- When `AUTH_DEV_BYPASS=true`, auth checks are skipped and requests execute as a stub user.

```yaml
openapi: 3.0.3
info:
  title: KidRide Backend
  version: "1.0.0"
servers:
  - url: /
paths:
  /health:
    get:
      summary: Health check
      responses:
        "200":
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok
                  service:
                    type: string
                    example: kidride-backend
  /api/v1/ping:
    get:
      summary: Ping
      responses:
        "200":
          description: Pong message
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: pong
  /api/v1/auth/login:
    post:
      summary: Login (client handles Firebase)
      description: Use Firebase client SDK to obtain an ID token; this endpoint echoes payload for debugging.
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
      responses:
        "200":
          description: Guidance response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/MessageResponse"
  /api/v1/auth/register:
    post:
      summary: Register (client handles Firebase)
      description: Registration occurs via Firebase; this endpoint echoes payload for debugging.
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
      responses:
        "200":
          description: Guidance response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/MessageResponse"
  /api/v1/users/me:
    get:
      summary: Get current user
      security:
        - bearerAuth: []
      responses:
        "200":
          description: Current user
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "401":
          description: Missing/invalid token
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "404":
          description: User not found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
  /api/v1/kids:
    post:
      summary: Create kid
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [first_name]
              properties:
                first_name:
                  type: string
                  example: Alex
                dob:
                  type: string
                  format: date
                  example: "2015-04-20"
                gender:
                  type: string
                  example: female
                avatar_url:
                  type: string
                  format: uri
                  example: https://example.com/avatar.png
                household_id:
                  type: string
                  description: If omitted, uses current user's household_id.
      responses:
        "201":
          description: Created kid
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Kid"
        "400":
          description: Validation error (e.g., missing first_name, invalid dob, missing household_id)
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
    get:
      summary: List kids for user/household
      security:
        - bearerAuth: []
      parameters:
        - in: query
          name: household_id
          schema:
            type: string
          description: Filter by household; defaults to current user's household_id, otherwise parent_user_id.
      responses:
        "200":
          description: Kids visible to the user
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Kid"
        "401":
          description: Missing/invalid token
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
  /api/v1/households:
    post:
      summary: Create household and optionally link current user
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [name]
              properties:
                name:
                  type: string
                  example: Smith Family
                address:
                  type: string
                  example: 123 Main St
                location:
                  type: string
                  example: Seattle, WA
      responses:
        "201":
          description: Created household
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Household"
        "400":
          description: Missing name
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
  /api/v1/households/me:
    get:
      summary: Get household for current user
      security:
        - bearerAuth: []
      responses:
        "200":
          description: Household linked to current user
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Household"
        "401":
          description: Missing/invalid token
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "404":
          description: Household not found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: Firebase ID token supplied as `Authorization: Bearer <idToken>`.
  schemas:
    MessageResponse:
      type: object
      properties:
        message:
          type: string
          example: Use Firebase client SDK to obtain ID token; send as Bearer token to protected endpoints.
        echo:
          type: object
          description: Echo of provided payload (if any).
    ErrorResponse:
      type: object
      properties:
        error:
          type: string
          example: Missing bearer token
        details:
          type: object
          nullable: true
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        firebase_uid:
          type: string
        email:
          type: string
          format: email
        first_name:
          type: string
        last_name:
          type: string
        avatar_url:
          type: string
          format: uri
    Kid:
      type: object
      properties:
        id:
          type: string
          format: uuid
        first_name:
          type: string
        gender:
          type: string
          nullable: true
        dob:
          type: string
          format: date
          nullable: true
        household_id:
          type: string
          nullable: true
        parent_user_id:
          type: string
          nullable: true
        avatar_url:
          type: string
          format: uri
          nullable: true
    Household:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        address:
          type: string
          nullable: true
        location:
          type: string
          nullable: true
```

