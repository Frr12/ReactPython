from typing import List, Optional, Tuple
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.logger import logger as fastapi_logger
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
logger = logging.getLogger("uvicorn")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)
logger.error("API Started")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/movies", response_model=List[schemas.Movie])
def read_all_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = crud.get_movies(db, skip=skip, limit=limit)
    return movies

@app.get("/movies/by_id/{movie_id}", response_model=schemas.MovieDetail)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie to read not found")
    return movie

@app.get("/movies/get_by_title", response_model=List[schemas.Movie])
def get_movies_by_title(mt: str, db: Session = Depends(get_db)):
    movies = crud.get_movies_by_title(db=db, movie_title=mt)
    if movies is None:
        raise HTTPException(status_code=404, detail="No movies found for this title")
    return movies

@app.get("/movies/get_by_range_year", response_model=List[schemas.Movie])
def get_movies_by_range_year(ymin: Optional[int] = None, ymax: Optional[int] = None, db: Session = Depends(get_db)):
    movies = crud.get_movies_by_range_year(db=db, year_min=ymin, year_max=ymax)
    return movies

@app.get("/movies/get_movies_by_director_name/{dr_name}", response_model=List[schemas.Movie])
def get_movies_by_director_name(dr_name: str, db: Session = Depends(get_db)):
    movies = crud.get_movies_by_director_name(db=db, director_name=dr_name)
    if movies is None:
        raise HTTPException(status_code=404, detail="No movies found for this director")
    return movies

@app.get("/movies/by_actor", response_model=List[schemas.Movie])
def read_movies_by_actor(n: str, db: Session = Depends(get_db)):
    movies = crud.get_movies_by_actor_endname(db=db, endname=n)
    if movies is None:
        raise HTTPException(status_code=404, detail="No movies found for this actor endname")
    return movies

@app.get("/movies/count_by_year", response_model=List[schemas.MovieStat])
def read_count_movies_by_year(db: Session = Depends(get_db)):
    return crud.get_count_movies_by_year(db=db)

@app.post("/movies", response_model=schemas.Movie)
def create_movie(movie : schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db=db, movie=movie)

@app.put("/movies/director", response_model=schemas.MovieDetail)
def update_movie_director(mid: int, sid: int, db: Session = Depends(get_db)):
    db_movie = crud.update_movie_director(db=db, movie_id=mid, director_id=sid)
    if db_movie is "error_m":
        raise HTTPException(status_code=404, detail=f"Movie not found for id {mid}")
    elif db_movie is "error_s":
        raise HTTPException(status_code=404, detail=f"Star not found for id {sid}")
    return db_movie

@app.post("/movies/actor", response_model=schemas.MovieDetail)
def add_movie_actor(mid: int, sid: int, db: Session = Depends(get_db)):
    db_movie = crud.add_movie_actor(db=db, movie_id=mid, star_id=sid)
    if db_movie is "error_m":
        raise HTTPException(status_code=404, detail=f"Movie not found for id {mid}")
    elif db_movie is "error_s":
        raise HTTPException(status_code=404, detail=f"Star not found for id {sid}")
    return db_movie

@app.put("/movies/actors", response_model=schemas.MovieDetail)
def update_movie_actors(mid: int, sids: List[int], db: Session = Depends(get_db)):
    db_movie = crud.update_movie_actors(db=db, movie_id=mid, star_ids=sids)
    if db_movie is None:
        raise HTTPException(status_code=404, detail=f"Movie not found for id {mid}")
    return db_movie

@app.put("/movies", response_model=schemas.Movie)
def update_movie(movie : schemas.Movie, db: Session = Depends(get_db)):
    return crud.update_movie(db=db, movie=movie)

@app.delete("/movies/by_id/{movie_id}", response_model=schemas.Movie)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    return crud.delete_movie(db=db, movie_id=movie_id)

@app.get("/stars", response_model=List[schemas.Star])
def read_stars(skip: Optional[int] = 0, limit: Optional[int] = 100, db: Session = Depends(get_db)):
    # read items from database
    stars = crud.get_stars(db, skip=skip, limit=limit)
    # return them as json
    return stars

@app.get("/stars/by_id/{star_id}", response_model=schemas.Star)
def read_star(star_id: int, db: Session = Depends(get_db)):
    db_star = crud.get_star(db, star_id=star_id)
    if db_star is None:
        raise HTTPException(status_code=404, detail="Star to read not found")
    return db_star

@app.get("/stars/by_name", response_model=List[schemas.Star])
def read_stars_by_name(n: str, db: Session = Depends(get_db)):
    # read items from database
    stars = crud.get_stars_by_name(db=db, name=n)
    if stars is None:
        raise HTTPException(status_code=404, detail="No star with this name")
    return stars

@app.get("/stars/by_endname", response_model=List[schemas.Star])
def read_stars_by_endname(n: str, db: Session = Depends(get_db)):
    # read items from database
    stars = crud.get_stars_by_endname(db=db, name=n)
    if stars is None:
        raise HTTPException(status_code=404, detail="No star with this endname")
    return stars

@app.get("/stars/by_birthyear/{year}", response_model=List[schemas.Star])
def read_stars_by_birthyear(year: int, db: Session = Depends(get_db)):
    stars = crud.get_stars_by_birthyear(db=db, year=year)
    if stars is None:
        raise HTTPException(status_code=404, detail="No actor for this year")
    return stars

@app.post("/stars", response_model=schemas.Star)
def create_star(star : schemas.StarCreate, db: Session = Depends(get_db)):
    return crud.create_star(db=db, star=star)

@app.put("/stars", response_model=schemas.Star)
def update_star(star : schemas.Star, db: Session = Depends(get_db)):
    return crud.update_star(db=db, star=star)

@app.delete("/stars/by_id/{star_id}", response_model=schemas.Star)
def delete_star(star_id: int, db: Session = Depends(get_db)):
    deleted_star = crud.delete_star(db=db, star_id=star_id)
    if delete_star is None:
        raise HTTPException(status_code=404, detail=f"Error in the deletion of star with id {star_id}")
    return crud.delete_star(db=db, star_id=star_id)

@app.get("/stars/get_director_by_id_movie/{movie_id}", response_model=schemas.Star)
def get_director_by_id_movie(movie_id: str, db: Session = Depends(get_db)):
    director = crud.get_director_by_id_movie(db=db, movie_id=movie_id)
    if director is None:
        raise HTTPException(status_code=404, detail="No director found for this movie id")
    return director

@app.get("/stars/get_director_by_movie_title", response_model=List[schemas.Star])
def get_director_by_movie_title(mt: str, db: Session = Depends(get_db)):
    director = crud.get_director_by_movie_title(db=db, movie_title=mt)
    if director is None:
        raise HTTPException(status_code=404, detail="No director found for this movie title")
    return director

@app.get("/stars/stats_movie_by_director")
def read_stats_movie_by_director(minc: Optional[int] = 10, db: Session = Depends(get_db)):
    stats = crud.get_stats_movie_by_director(db=db, min_count=minc)
    if stats is None:
        raise HTTPException(status_code=404, detail="Error in the recuperation of statistics about directors")
    return stats

@app.get("/stars/stats_movie_by_actor", response_model=List[schemas.ActorStat])
def read_stats_movie_by_actor(minc: Optional[int] = 10, db: Session = Depends(get_db)):
    stats = crud.get_stats_movie_by_actor(db=db, min_count=minc)
    if stats is None:
        raise HTTPException(status_code=404, detail="Error in the recuperation of statistics about actors")
    return stats

