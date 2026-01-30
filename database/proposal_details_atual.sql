USE [crm_db]
GO

SELECT [id]
      ,[proposal_id]
      ,[product_name]
      ,[type_name]
      ,[team_name]
      ,[value]
      ,[license_of_use]
      ,[training]
      ,[monthly_fee]
      ,[professional_services]
      ,[monthly_fee_annualized]
      ,[total_sales]
  FROM [dbo].[proposal_details]

GO


