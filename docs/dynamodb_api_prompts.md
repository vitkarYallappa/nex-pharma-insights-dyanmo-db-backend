# DynamoDB Code & Table Generation Prompts

# API Implementation Specification

- Implement **create**, **get_by_id**, and **get_all_by_query** APIs.  
- Provide implementations in **route**, **controller**, **service**, and **repository** layers.  
- Use the existing **table implementation** as the base.  
- Do not introduce any new coding style or format.  
- Maintain strict consistency so other developers are not confused.  

## Repository
- `create`  
- `find_one_by_query`  
- `find_all_by_query`  
- `get_all_projects`  
- `update_project`  

## Service
- `create_project`  
- `get_project_by_id`  
- `get_projects_by_query`  
- `update_project`  

## Controller
- `create_project`  
- `get_project_by_id`  
- `get_projects_by_query`  

## Routes
- `POST /`  
- `GET /{id}`  
- `GET /` (with query params)  

---
✅ Ensure the same structure and naming conventions.  
✅ When creating methods for other tables, replace **project** with the respective table name (e.g., **employee**). 

## Prompt 2: SQLAlchemy → DynamoDB Conversion (6 lines)
1. Convert the given **SQLAlchemy table code** into **DynamoDB code**.  
2. Use the **existing table implementation** as the base.  
3. Do **not** introduce any new coding style or format.  
4. Follow the **same structure and conventions** already in use.  
5. Keep the code **consistent** so other developers won’t get confused.  
6. Ensure only the necessary **table logic changes** for DynamoDB are applied.

