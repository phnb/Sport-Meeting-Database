use sport_meeting_management_system;


-- 每个书院总报名记录数
-- select College_name from player, event_has_player where player.Player_id = event_has_player.Player_id;
-- SELECT * FROM sport_meeting_management_system.player;
-- REALCASE:::

-- with total_colls(College_name) as (
-- 	select College_name from player, event_has_player where player.Player_id = event_has_player.Player_id
-- )
-- select count(*) as par_records, College_name from total_colls as records_coll group by College_name;

-- 每个书院总参与人数
-- 假设：每个书院都有人参赛
-- with distinct_id(id) as (select distinct Player_id from event_has_player)
-- select College_name from player, distinct_id where player.Player_id = distinct_id.id;

-- select count(*) as par_people, College_name from (
-- 	with distinct_id(id) as (
-- 		select distinct Player_id from event_has_player
--     )
-- 	select College_name from player, distinct_id where player.Player_id = distinct_id.id
-- ) as popu_coll group by College_name;
-- 书院参与记录和参与人数和比例总表
-- 人数和记录数重要性比例：7:3








-- Assumptions:
-- 1. Every college has some participants
-- 2. The importance ratio between the number of people and the number of records = 7:3
select College_name, par_records, par_people, Population, 
	(par_records*0.3+par_people*0.7)/(Population*0.7+4*Population*0.3) -- Calculating the engagement rate
    as Engagement_rate from 
    ( 
    -- Calculate and select the total number of records
	with total_colls(College_name) as ( 
		select College_name from player, event_has_player where 
        player.Player_id = event_has_player.Player_id AND Event_has_player.Event_round = 1
	)
	select count(*) as par_records, 
		College_name from total_colls as records_coll group by College_name
) as population_coll 
natural join (
	-- Natural join with the number of participants calculated and selected (<= the number of records)
	select count(*) as par_people, College_name from (
		with distinct_id(id) as (
			select distinct Player_id from event_has_player
		)
		select College_name from player, distinct_id where player.Player_id = distinct_id.id
	) as popu_coll group by College_name
) as records_coll
natural join (
	-- Including the information of college population
	select College_name, Population from college
) as total_coll_popu
;





-- 外表数据补齐：from里用natural join处理
-- 本表分析：select里选改




