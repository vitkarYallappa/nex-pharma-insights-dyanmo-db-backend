# DynamoDB Code & Table Generation Prompts

## Prompt 1: API Implementation (10 lines)
1. Implement **create**, **get_by_id**, and **get_all_by_query** APIs.  
2. Provide implementations in **route, controller, service, and repository** layers.  
3. Use the **existing table implementation** as the base.  
4. Do **not** introduce any new coding style or format.  
5. Maintain strict **consistency** so other developers are not confused.  
6. ✅ **Repository**: create, find_one_by_query, find_all_by_query, get_all_projects, update_project.  
7. ✅ **Service**: create_project, get_project_by_id, get_projects_by_query, update_project.  
8. ✅ **Controller**: create_project, get_project_by_id, get_projects_by_query.  
9. ✅ **Routes**: POST `/`, GET `/{id}`, GET `/` (with query params).  
10. Ensure all layers follow the same structure and naming conventions already present.  

---

## Prompt 2: SQLAlchemy → DynamoDB Conversion (6 lines)
1. Convert the given **SQLAlchemy table code** into **DynamoDB code**.  
2. Use the **existing table implementation** as the base.  
3. Do **not** introduce any new coding style or format.  
4. Follow the **same structure and conventions** already in use.  
5. Keep the code **consistent** so other developers won’t get confused.  
6. Ensure only the necessary **table logic changes** for DynamoDB are applied.

