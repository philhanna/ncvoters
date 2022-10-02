CREATE VIEW active_voters as
	SELECT		*
	FROM		voters
	WHERE		status_cd = "A"
