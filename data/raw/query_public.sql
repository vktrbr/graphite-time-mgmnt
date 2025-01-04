select key
     , created
     , fields:status.name::text                                  as status
     , fields:assignee.emailAddress::text                        as assignee
     , fields:timeestimate::int                                  as time_estimate
     , fields:timeoriginalestimate::int                          as time_original_estimate
     , fields:summary::text                                      as summary

     , fields:issuetype.name::text                               as issue_type
     // Some custom fields for the sub-tasks description
     , fields:customfield_12039.content[0].content[0].text::text as what_to_todo
     , fields:customfield_12040.content[0].content[0].text::text as why_to_do

     , fields:description                                        as description

     , level_order
     , join_date

from {JIRA_TABLE}.issues
         left join {EMPLOYEES_TABLE} on assignee = email
where {ASSIGNEES_FILTER}
  and status = 'DONE'
  and issue_type in ('Advanced sub-task', 'Task');
