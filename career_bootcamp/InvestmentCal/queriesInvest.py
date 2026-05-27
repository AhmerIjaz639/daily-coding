add_in_investment ="""
               INSERT INTO investments
                   (asset_name, asset_type, buy_price, quantity, buy_date, current_price)
               VALUES (%s, %s, %s, %s, %s, %s)
           """

get_all_investments_db="""
              select 
                  id,
                  asset_name,
                  asset_type,
                  buy_price,
                  quantity,
                  buy_date,
                  current_price,
                  last_updated,
                  (quantity*buy_price)as invested,
                  (current_price*quantity)as current_value,
                  (quantity*current_price)-(quantity*buy_price)as profit_loss,
                  (profit/buy_price)*100 as profit_percentage
              from investments
                  ORDER BY profit_percentage DESC
"""