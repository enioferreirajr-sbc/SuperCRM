USE [crm_db]
GO

SELECT [id]
      ,[proposal_id]
      ,[customer_name]
      ,[proposal_name]
      ,[status]
      ,[closing_date]
      ,[total_value]
      ,[main_contract_id]
      ,[customer_reference]
      ,[business_proposal_date]
      ,[last_status_date]
      ,[funnel_percentage]
      ,[last_note]
  FROM [dbo].[proposals]

GO


