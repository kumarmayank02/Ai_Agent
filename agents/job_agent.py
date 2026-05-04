def build_smart_query(job_title, location, experience, job_types):
    """
    Smart query generator (Agent thinking)
    """

    query = f"{job_title} jobs in {location}"

    # 🔥 add intelligence
    if experience == 0:
        query += " fresher entry level"
    elif experience <= 2:
        query += " junior"
    else:
        query += f" {experience}+ years experience"

    if job_types:
        query += " " + " ".join(job_types)

    # 🔥 boost keywords
    query += " hiring now"

    return query


def rank_jobs(jobs, job_title):
    """
    Simple ranking logic (Agent decision)
    """

    scored_jobs = []

    for job in jobs:
        score = 0

        # 🎯 title match
        if job_title.lower() in job["Title"].lower():
            score += 50

        # 🎯 recent jobs boost
        if "day" in str(job.get("Posted", "")).lower():
            score += 20

        # 🎯 platform boost
        if job.get("Platform") == "LinkedIn":
            score += 10

        job["score"] = score
        scored_jobs.append(job)

    # 🔥 sort by score
    scored_jobs = sorted(scored_jobs, key=lambda x: x["score"], reverse=True)

    return scored_jobs