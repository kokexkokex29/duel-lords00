"""
Match Commands for DUEL LORDS Discord Bot
Enhanced duel system with private messaging and automatic reminders
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import re
import uuid

class MatchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="duel", description="Challenge players to a duel - /duel @player1 @player2 hour minute")
    @app_commands.describe(
        player1="First player",
        player2="Second player", 
        hour="Hour (0-23)",
        minute="Minute (0-59)"
    )
    async def create_duel(
        self, 
        interaction: discord.Interaction,
        player1: discord.Member,
        player2: discord.Member,
        hour: int,
        minute: int
    ):
        """Create a new duel between two players"""
        
        # Validate hour and minute
        if not (0 <= hour <= 23):
            await interaction.response.send_message(
                "❌ Hour must be between 0 and 23", 
                ephemeral=True
            )
            return
            
        if not (0 <= minute <= 59):
            await interaction.response.send_message(
                "❌ Minute must be between 0 and 59", 
                ephemeral=True
            )
            return

        # Check if both players are registered
        player1_data = self.db.get_player(str(player1.id))
        player2_data = self.db.get_player(str(player2.id))

        if not player1_data:
            await interaction.response.send_message(
                f"❌ {player1.display_name} is not registered for the tournament. They must use `/register` first",
                ephemeral=True
            )
            return

        if not player2_data:
            await interaction.response.send_message(
                f"❌ {player2.display_name} is not registered for the tournament. They must use `/register` first",
                ephemeral=True
            )
            return

        # Check if trying to duel the same person
        if player1.id == player2.id:
            await interaction.response.send_message(
                "❌ A player cannot duel themselves!",
                ephemeral=True
            )
            return

        # Create scheduled time for today at specified hour:minute
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has passed today, schedule for tomorrow
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)

        # Create match in database
        match_id = str(uuid.uuid4())[:8]
        match_data = {
            'id': match_id,
            'player1_id': str(player1.id),
            'player2_id': str(player2.id),
            'scheduled_time': scheduled_time.isoformat(),
            'status': 'scheduled',
            'channel_id': str(interaction.channel.id) if interaction.channel else None,
            'created_by': str(interaction.user.id),
            'created_at': datetime.now().isoformat(),
            'reminder_sent': False
        }

        # Save to database
        self.db.create_match(
            challenger_id=str(player1.id),
            opponent_id=str(player2.id),
            scheduled_time=scheduled_time.isoformat(),
            description=f"Duel between {player1.display_name} and {player2.display_name}"
        )

        # Create main embed for channel
        embed = discord.Embed(
            title="⚔️ New Duel Scheduled!",
            description="A new duel has been created successfully",
            color=0xFFD700,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="🥊 Fighters",
            value=f"{player1.mention} **VS** {player2.mention}",
            inline=False
        )

        embed.add_field(
            name="🕐 Duel Time",
            value=f"<t:{int(scheduled_time.timestamp())}:F>\n<t:{int(scheduled_time.timestamp())}:R>",
            inline=False
        )

        embed.add_field(
            name="🌐 Server Info",
            value="**IP:** `18.228.228.44`\n**Port:** `3827`",
            inline=True
        )

        embed.add_field(
            name="🆔 Match ID",
            value=f"`{match_id}`",
            inline=True
        )

        embed.add_field(
            name="📋 Important Notes",
            value="• Reminder will be sent 5 minutes before match\n• Private message will be sent to both players\n• Use `/report_result` to record the result",
            inline=False
        )

        embed.set_footer(text="DUEL LORDS • Ready for battle!")

        # Send to channel
        await interaction.response.send_message(
            f"🚨 **New Duel!** {player1.mention} vs {player2.mention}",
            embed=embed
        )

        # Send private messages to both players
        await self.send_duel_notification_dm(player1, player2, scheduled_time, match_id)
        await self.send_duel_notification_dm(player2, player1, scheduled_time, match_id)

    async def send_duel_notification_dm(self, player, opponent, scheduled_time, match_id):
        """Send private message notification about the duel"""
        try:
            embed = discord.Embed(
                title="🎮 New Duel Scheduled!",
                description=f"You have a scheduled duel against **{opponent.display_name}**",
                color=0x00FF00,
                timestamp=datetime.now()
            )

            embed.add_field(
                name="⚔️ Opponent",
                value=f"{opponent.mention} ({opponent.display_name})",
                inline=True
            )

            embed.add_field(
                name="🕐 الموعد",
                value=f"<t:{int(scheduled_time.timestamp())}:F>",
                inline=True
            )

            embed.add_field(
                name="⏰ متبقي",
                value=f"<t:{int(scheduled_time.timestamp())}:R>",
                inline=True
            )

            embed.add_field(
                name="🌐 معلومات الاتصال",
                value="**IP:** `18.228.228.44`\n**Port:** `3827`",
                inline=False
            )

            embed.add_field(
                name="📝 تعليمات",
                value="• ادخل إلى لعبة BombSquad\n• اتصل بالخادم باستخدام المعلومات أعلاه\n• ستحصل على تذكير قبل المبارزة بـ 5 دقائق",
                inline=False
            )

            embed.add_field(
                name="🆔 معرف المبارزة",
                value=f"`{match_id}`",
                inline=False
            )

            embed.set_footer(text="DUEL LORDS • حظاً موفقاً في المبارزة!")

            await player.send(embed=embed)
            print(f"✅ دعوة المبارزة أرسلت إلى {player.display_name}")

        except discord.Forbidden:
            print(f"❌ لا يمكن إرسال رسالة خاصة إلى {player.display_name}")
        except Exception as e:
            print(f"❌ خطأ في إرسال الرسالة الخاصة إلى {player.display_name}: {e}")

    @app_commands.command(name="record_result", description="تسجيل نتيجة مبارزة")
    @app_commands.describe(
        match_id="معرف المبارزة",
        winner="الفائز في المبارزة",
        winner_kills="عدد قتل الفائز (افتراضي: 0)",
        loser_kills="عدد قتل الخاسر (افتراضي: 0)"
    )
    async def record_match_result(
        self,
        interaction: discord.Interaction,
        match_id: str,
        winner: discord.Member,
        winner_kills: int = 0,
        loser_kills: int = 0
    ):
        """Record the result of a completed match"""
        
        # Get match data
        match = self.db.get_match(match_id)
        if not match:
            await interaction.response.send_message(
                f"❌ لا توجد مبارزة بالمعرف `{match_id}`",
                ephemeral=True
            )
            return

        player1_id = str(match['player1_id'])
        player2_id = str(match['player2_id'])
        winner_id = str(winner.id)

        # Check if winner is one of the participants
        if winner_id not in [player1_id, player2_id]:
            await interaction.response.send_message(
                "❌ الفائز يجب أن يكون أحد المشاركين في المبارزة",
                ephemeral=True
            )
            return

        # Determine loser
        loser_id = player2_id if winner_id == player1_id else player1_id

        # Validate kill counts
        if winner_kills < 0 or loser_kills < 0:
            await interaction.response.send_message(
                "❌ عدد القتل يجب أن يكون 0 أو أكثر",
                ephemeral=True
            )
            return

        # Record the result
        result_data = {
            'winner_id': winner_id,
            'loser_id': loser_id,
            'winner_kills': winner_kills,
            'loser_kills': loser_kills,
            'completed_at': datetime.now().isoformat()
        }

        success = self.db.record_match_result(match_id, result_data)
        
        if not success:
            await interaction.response.send_message(
                "❌ فشل في تسجيل نتيجة المبارزة",
                ephemeral=True
            )
            return

        # Update player statistics
        self.db.update_player_stats(int(winner_id), wins=1, kills=winner_kills, deaths=loser_kills)
        self.db.update_player_stats(int(loser_id), losses=1, kills=loser_kills, deaths=winner_kills)

        # Get player data for names
        winner_data = self.db.get_player(winner_id)
        loser_data = self.db.get_player(loser_id)
        winner_name = winner_data.get('name', winner.display_name) if winner_data else winner.display_name
        loser_name = loser_data.get('name', 'مجهول') if loser_data else 'مجهول'

        # Create result embed
        embed = discord.Embed(
            title="🏆 نتيجة المبارزة",
            description="تم تسجيل نتيجة المبارزة بنجاح!",
            color=0x43B581,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="🥇 الفائز",
            value=f"**{winner_name}** {winner.mention}",
            inline=True
        )

        embed.add_field(
            name="💀 الخاسر", 
            value=f"**{loser_name}** <@{loser_id}>",
            inline=True
        )

        embed.add_field(
            name="📊 الإحصائيات",
            value=f"**{winner_name}:** {winner_kills} قتل\n**{loser_name}:** {loser_kills} قتل",
            inline=False
        )

        embed.add_field(
            name="🆔 معرف المبارزة",
            value=f"`{match_id}`",
            inline=True
        )

        embed.set_footer(text="DUEL LORDS • معركة رائعة!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="matches", description="عرض المباريات المجدولة")
    async def show_matches(self, interaction: discord.Interaction):
        """Show upcoming scheduled matches"""
        
        matches = self.db.get_upcoming_matches()
        
        if not matches:
            embed = discord.Embed(
                title="📅 المباريات المجدولة",
                description="لا توجد مباريات مجدولة حالياً",
                color=0xFAA61A
            )
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            title="📅 المباريات المجدولة",
            description=f"إجمالي {len(matches)} مبارزة مجدولة",
            color=0x00D4FF,
            timestamp=datetime.now()
        )

        for i, match in enumerate(matches[:10], 1):  # Show max 10 matches
            try:
                scheduled_time = datetime.fromisoformat(match['scheduled_time'])
                player1_data = self.db.get_player(match['player1_id'])
                player2_data = self.db.get_player(match['player2_id'])
                
                player1_name = player1_data.get('name', f"Player {match['player1_id']}") if player1_data else f"Player {match['player1_id']}"
                player2_name = player2_data.get('name', f"Player {match['player2_id']}") if player2_data else f"Player {match['player2_id']}"
                
                embed.add_field(
                    name=f"⚔️ مبارزة #{i}",
                    value=f"**{player1_name}** vs **{player2_name}**\n"
                          f"🕐 <t:{int(scheduled_time.timestamp())}:R>\n"
                          f"🆔 `{match['id']}`",
                    inline=True
                )
            except:
                continue

        embed.set_footer(text="استخدم /record_result لتسجيل نتائج المباريات")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cancel_match", description="إلغاء مبارزة مجدولة")
    @app_commands.describe(match_id="معرف المبارزة المراد إلغاؤها")
    async def cancel_match(self, interaction: discord.Interaction, match_id: str):
        """Cancel a scheduled match"""
        
        match = self.db.get_match(match_id)
        if not match:
            await interaction.response.send_message(
                f"❌ لا توجد مبارزة بالمعرف `{match_id}`",
                ephemeral=True
            )
            return

        # Check if user is authorized to cancel
        user_id = str(interaction.user.id)
        if (user_id != match['player1_id'] and 
            user_id != match['player2_id'] and 
            not (isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions.administrator)):
            await interaction.response.send_message(
                "❌ يمكن فقط للمشاركين في المبارزة أو المشرفين إلغاؤها",
                ephemeral=True
            )
            return

        # Cancel the match
        success = self.db.cancel_match(match_id)
        
        if success:
            embed = discord.Embed(
                title="✅ تم إلغاء المبارزة",
                description=f"تم إلغاء المبارزة `{match_id}` بنجاح",
                color=0x43B581
            )
            
            embed.add_field(
                name="⚔️ المتبارزون",
                value=f"<@{match['player1_id']}> vs <@{match['player2_id']}>",
                inline=False
            )
            
            embed.add_field(
                name="👤 ألغيت بواسطة",
                value=interaction.user.mention,
                inline=True
            )
        else:
            embed = discord.Embed(
                title="❌ فشل الإلغاء",
                description="حدث خطأ أثناء إلغاء المبارزة",
                color=0xF04747
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="record_result", description="Record the result of a match")
    @app_commands.describe(
        match_id="Match ID to record result for",
        winner="Winner of the match",
        loser="Loser of the match",
        winner_kills="Winner's kill count",
        loser_kills="Loser's kill count"
    )
    async def record_result(
        self, 
        interaction: discord.Interaction,
        match_id: str,
        winner: discord.Member,
        loser: discord.Member,
        winner_kills: int = 0,
        loser_kills: int = 0
    ):
        """Record match result and update player statistics"""
        
        # Get match data
        match = self.db.get_match(match_id)
        if not match:
            await interaction.response.send_message(
                f"❌ Match with ID `{match_id}` not found",
                ephemeral=True
            )
            return
        
        # Verify participants
        participants = [match['player1_id'], match['player2_id']]
        if str(winner.id) not in participants or str(loser.id) not in participants:
            await interaction.response.send_message(
                "❌ Both winner and loser must be participants in this match",
                ephemeral=True
            )
            return
        
        # Update match status
        match['status'] = 'completed'
        match['winner_id'] = str(winner.id)
        match['completed_at'] = datetime.now().isoformat()
        match['winner_kills'] = winner_kills
        match['loser_kills'] = loser_kills
        
        self.db.update_match(match_id, match)
        
        # Update player statistics
        self.db.update_player_stats(str(winner.id), wins=1, kills=winner_kills)
        self.db.update_player_stats(str(loser.id), losses=1, kills=loser_kills)
        
        # Create result embed
        embed = discord.Embed(
            title="📊 Match Result Recorded",
            description=f"Results for match `{match_id}` have been saved",
            color=0x00FF00,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🏆 Winner", 
            value=f"{winner.mention}\n⚔️ {winner_kills} kills", 
            inline=True
        )
        
        embed.add_field(
            name="💀 Loser", 
            value=f"{loser.mention}\n⚔️ {loser_kills} kills", 
            inline=True
        )
        
        embed.add_field(
            name="📈 Stats Updated",
            value="Player statistics have been updated automatically",
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • Good game!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="matches", description="Show scheduled matches")
    async def show_matches(self, interaction: discord.Interaction):
        """Show all scheduled matches"""
        matches = self.db.get_all_matches()
        
        if not matches:
            embed = discord.Embed(
                title="📅 No Matches Scheduled",
                description="No matches are currently scheduled",
                color=0xFAA61A
            )
            embed.add_field(
                name="💡 How to Schedule",
                value="Use `/duel @player1 @player2 hour minute` to create a match",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Filter active matches
        active_matches = [m for m in matches.values() if m['status'] in ['scheduled', 'accepted']]
        
        embed = discord.Embed(
            title="📅 Scheduled Matches",
            description=f"Total: {len(active_matches)} active matches",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        for match in active_matches[:10]:  # Show first 10
            try:
                player1 = await interaction.client.fetch_user(int(match['player1_id']))
                player2 = await interaction.client.fetch_user(int(match['player2_id']))
                
                scheduled_time = datetime.fromisoformat(match['scheduled_time'])
                time_str = f"<t:{int(scheduled_time.timestamp())}:R>"
                
                embed.add_field(
                    name=f"Match {match['id']}",
                    value=f"{player1.display_name} vs {player2.display_name}\n🕐 {time_str}",
                    inline=True
                )
            except:
                continue
        
        if len(active_matches) > 10:
            embed.add_field(
                name="📊 More Matches",
                value=f"And {len(active_matches) - 10} more matches...",
                inline=False
            )
        
        embed.set_footer(text="DUEL LORDS • Use /record_result to submit results")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cancel_match", description="Cancel a scheduled match")
    @app_commands.describe(match_id="Match ID to cancel")
    async def cancel_match(self, interaction: discord.Interaction, match_id: str):
        """Cancel a scheduled match"""
        match = self.db.get_match(match_id)
        
        if not match:
            await interaction.response.send_message(
                f"❌ Match with ID `{match_id}` not found",
                ephemeral=True
            )
            return
        
        # Check if user is participant or admin
        user_id = str(interaction.user.id)
        is_participant = user_id in [match['player1_id'], match['player2_id']]
        is_admin = (isinstance(interaction.user, discord.Member) and 
                   interaction.user.guild_permissions.administrator)
        
        if not (is_participant or is_admin):
            await interaction.response.send_message(
                "❌ Only match participants or administrators can cancel matches",
                ephemeral=True
            )
            return
        
        if match['status'] == 'completed':
            await interaction.response.send_message(
                "❌ Cannot cancel a completed match",
                ephemeral=True
            )
            return
        
        # Cancel the match
        match['status'] = 'cancelled'
        match['cancelled_at'] = datetime.now().isoformat()
        match['cancelled_by'] = user_id
        
        self.db.update_match(match_id, match)
        
        embed = discord.Embed(
            title="❌ Match Cancelled",
            description=f"Match `{match_id}` has been cancelled",
            color=0xFF6B6B,
            timestamp=datetime.now()
        )
        
        try:
            player1 = await interaction.client.fetch_user(int(match['player1_id']))
            player2 = await interaction.client.fetch_user(int(match['player2_id']))
            
            embed.add_field(
                name="🥊 Match",
                value=f"{player1.display_name} vs {player2.display_name}",
                inline=False
            )
        except:
            pass
        
        embed.add_field(
            name="🗑️ Cancelled by",
            value=interaction.user.display_name,
            inline=True
        )
        
        embed.set_footer(text="DUEL LORDS • Match cancelled")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MatchCommands(bot))