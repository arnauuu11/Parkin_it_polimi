# src/parkin_web/crud/user.py (continued)
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the user
            
        Returns:
            The created user instance
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            bio=obj_in.bio,
            user_type=obj_in.user_type,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user.
        
        Args:
            db: Database session
            db_obj: User instance to update
            obj_in: Schema or dict containing the data to update
            
        Returns:
            The updated user instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session
            email: Email of the user to authenticate
            password: Password to verify
            
        Returns:
            The authenticated user instance if successful, None otherwise
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
        
    def is_active(self, user: User) -> bool:
        """
        Check if a user is active.
        
        Args:
            user: User instance to check
            
        Returns:
            True if the user is active, False otherwise
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        Check if a user is a superuser.
        
        Args:
            user: User instance to check
            
        Returns:
            True if the user is a superuser, False otherwise
        """
        return user.is_superuser
    
    def update_profile(
        self, db: Session, *, user_id: int, profile_data: Dict[str, Any]
    ) -> User:
        """
        Update a user's profile.
        
        Args:
            db: Database session
            user_id: ID of the user to update
            profile_data: Dict containing the profile data to update
            
        Returns:
            The updated user instance
        """
        user = self.get(db, id=user_id)
        return self.update(db, db_obj=user, obj_in=profile_data)
    
    def get_users_by_type(
        self, db: Session, *, user_type: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get users by type.
        
        Args:
            db: Database session
            user_type: Type of users to get
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of user instances
        """
        return db.query(User).filter(User.user_type == user_type).offset(skip).limit(limit).all()

    def update_rating(self, db: Session, *, id: int, rating: int) -> None:
        """
        Update the average rating for a user.
        
        Args:
            db: Database session
            id: ID of the user
            rating: New rating to add (1-5)
        """
        user = db.query(User).filter(User.id == id).first()
        if user:
            # Update the average rating
            total_ratings = user.total_ratings
            current_average = user.rating
            
            new_total = total_ratings + 1
            new_average = ((current_average * total_ratings) + rating) / new_total
            
            user.total_ratings = new_total
            user.rating = new_average
            
            db.add(user)
            db.commit()


user = CRUDUser(User)