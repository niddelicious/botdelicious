import logging
from datetime import timedelta

from helpers.Dataclasses import OBSText
from helpers.SessionData import SessionData


def test_session_data():
    logging.basicConfig(level=logging.DEBUG)

    # Start session
    SessionData.start_session()

    # Set current track
    SessionData.set_current_track("The Beatles", "Let It Be")

    # Add some data to the session
    SessionData.add_comment()
    SessionData.add_raid("user1", 10)
    SessionData.add_follower("user2")
    SessionData.add_moderator("user3")
    SessionData.add_vip("user4")
    SessionData.add_tokens(100)

    # Get session info
    start_time = SessionData.get_session_start()
    current_track = SessionData.get_current_track()
    playlist = SessionData.get_playlist()
    comments_count = SessionData.comments_count()
    raids_count = SessionData.raids_count()
    followers_count = SessionData.followers_count()
    moderators_count = SessionData.moderators_count()
    vips_count = SessionData.vips_count()
    tokens_count = SessionData.tokens_count()

    # Print session info
    print(f"Session started at: {start_time}")
    print(f"Current track: {current_track.artist} - {current_track.title}")
    print(f"Playlist: {playlist}")
    print(f"Comments count: {comments_count}")
    print(f"Raids count: {raids_count}")
    print(f"Followers count: {followers_count}")
    print(f"Moderators count: {moderators_count}")
    print(f"VIPs count: {vips_count}")
    print(f"Tokens count: {tokens_count}")

    # Write playlist to file
    SessionData.write_playlist_to_file()

    # Process session credits
    credits = SessionData.process_session_credits()
    for credit in credits:
        print(credit)

    # Verify session data
    assert current_track.artist == "The Beatles"
    assert current_track.title == "Let It Be"
    assert len(playlist) == 1
    assert comments_count == 1
    assert raids_count == 1
    assert followers_count == 1
    assert moderators_count == 1
    assert vips_count == 1
    assert tokens_count == 100

    # Advance time and add another track to playlist
    SessionData.set_current_track("Pink Floyd", "Comfortably Numb")
    SessionData.add_tokens(50)
    SessionData.add_current_track_to_session_playlist()

    # Get updated session info
    updated_playlist = SessionData.get_playlist()
    updated_tokens_count = SessionData.tokens_count()

    # Verify updated session data
    assert len(updated_playlist) == 2
    assert updated_tokens_count == 150

    # Write updated playlist to file
    SessionData.write_playlist_to_file()

    # Process updated session credits
    updated_credits = SessionData.process_session_credits()
    for credit in updated_credits:
        print(credit)

