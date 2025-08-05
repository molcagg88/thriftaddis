from sqlmodel import select
from datetime import datetime, timezone
import asyncio
from db.models import Auction, Status
from db.main import get_db_session

async def update_auction_statuses():
    while True:
        try:
            async with get_db_session() as session:
                now = datetime.now(timezone.utc)

                # Ended auctions
                result = await session.exec(
                    select(Auction).where(
                        Auction.status != "ended",
                        Auction.ending_time < now
                    )
                )
                for auction in result.all():
                    auction.status = Status.ended

                # Live auctions
                result = await session.exec(
                    select(Auction).where(
                        Auction.status != "live",
                        Auction.starting_time <= now,
                        Auction.ending_time > now
                    )
                )
                for auction in result:
                    auction.status = Status.live

                await session.commit()
                print("Auction statuses updated.")

        except Exception as e:
            print("Error updating auction statuses:", e)

        await asyncio.sleep(60)  # wait 60 seconds before checking again

async def update_auction_statuses_once():
    try:
        async with get_db_session() as session:
            now = datetime.now(timezone.utc)

            # Ended auctions
            result = await session.exec(
                select(Auction).where(
                    Auction.status != "ended",
                    Auction.ending_time < now
                )
            )
            for auction in result.all():
                auction.status = Status.ended

            # Live auctions
            result = await session.exec(
                select(Auction).where(
                    Auction.status != "live",
                    Auction.starting_time <= now,
                    Auction.ending_time > now
                )
            )
            for auction in result:
                auction.status = Status.live

            await session.commit()
            print("\nAuction statuses updated.\n")

    except Exception as e:
        print("Error updating auction statuses:", e)

