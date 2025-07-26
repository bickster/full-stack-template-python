#!/usr/bin/env python3
"""
FullStack API CLI Example

A command-line interface for interacting with the FullStack API.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

# Add the SDK to the path if running from examples directory
sdk_path = Path(__file__).parent.parent.parent / "sdk" / "python" / "src"
if sdk_path.exists():
    sys.path.insert(0, str(sdk_path))

from fullstack_api import (
    FullStackClient,
    FileTokenStorage,
    LoginRequest,
    RegisterRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
    AuthenticationError,
    ValidationError,
    RateLimitError,
)

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()

# API client configuration
API_URL = os.getenv("FULLSTACK_API_URL", "http://localhost:8000")
TOKEN_FILE = Path.home() / ".fullstack" / "cli_tokens.json"


def get_client() -> FullStackClient:
    """Get API client with file-based token storage."""
    return FullStackClient(API_URL, token_storage=FileTokenStorage(str(TOKEN_FILE)))


@click.group()
def cli():
    """FullStack API Command Line Interface"""
    pass


@cli.command()
def login():
    """Login to the API"""
    client = get_client()
    
    # Check if already logged in
    if client.is_authenticated():
        try:
            user = client.get_current_user()
            rprint(f"[green]Already logged in as {user.username}[/green]")
            if not Confirm.ask("Do you want to login as a different user?"):
                return
        except:
            pass
    
    username = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)
    
    try:
        with console.status("Logging in..."):
            client.login(LoginRequest(username=username, password=password))
            user = client.get_current_user()
        
        rprint(f"[green]✓ Successfully logged in as {user.username}![/green]")
        
    except AuthenticationError as e:
        rprint(f"[red]✗ Login failed: {e.message}[/red]")
        sys.exit(1)
    except RateLimitError as e:
        retry_after = e.retry_after or 900
        rprint(f"[red]✗ Too many login attempts. Try again in {retry_after} seconds.[/red]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def logout():
    """Logout from the API"""
    client = get_client()
    
    if not client.is_authenticated():
        rprint("[yellow]Not logged in[/yellow]")
        return
    
    try:
        with console.status("Logging out..."):
            client.logout()
        rprint("[green]✓ Successfully logged out[/green]")
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        # Clear tokens anyway
        client.clear_tokens()


@cli.command()
def register():
    """Register a new account"""
    client = get_client()
    
    rprint("[bold]Register New Account[/bold]")
    
    email = Prompt.ask("Email")
    username = Prompt.ask("Username")
    full_name = Prompt.ask("Full Name (optional)", default="")
    password = Prompt.ask("Password", password=True)
    confirm_password = Prompt.ask("Confirm Password", password=True)
    
    if password != confirm_password:
        rprint("[red]✗ Passwords do not match[/red]")
        sys.exit(1)
    
    try:
        with console.status("Creating account..."):
            user = client.register(RegisterRequest(
                email=email,
                username=username,
                password=password,
                full_name=full_name if full_name else None
            ))
        
        rprint(f"[green]✓ Account created successfully![/green]")
        
        # Auto-login
        if Confirm.ask("Do you want to login now?", default=True):
            with console.status("Logging in..."):
                client.login(LoginRequest(username=username, password=password))
            rprint(f"[green]✓ Logged in as {username}[/green]")
            
    except ValidationError as e:
        rprint("[red]✗ Validation errors:[/red]")
        for error in e.errors:
            rprint(f"  - {error['field']}: {error['message']}")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def whoami():
    """Show current user information"""
    client = get_client()
    
    if not client.is_authenticated():
        rprint("[yellow]Not logged in[/yellow]")
        rprint("Use 'fullstack-cli login' to authenticate")
        return
    
    try:
        with console.status("Fetching user information..."):
            user = client.get_current_user()
        
        # Create a table for user info
        table = Table(title="User Information", show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        
        table.add_row("ID", user.id)
        table.add_row("Username", user.username)
        table.add_row("Email", user.email)
        table.add_row("Full Name", user.full_name or "[dim]Not set[/dim]")
        table.add_row("Active", "[green]Yes[/green]" if user.is_active else "[red]No[/red]")
        table.add_row("Verified", "[green]Yes[/green]" if user.is_verified else "[yellow]No[/yellow]")
        table.add_row("Superuser", "[green]Yes[/green]" if user.is_superuser else "No")
        table.add_row("Created", str(user.created_at))
        table.add_row("Updated", str(user.updated_at))
        
        console.print(table)
        
    except AuthenticationError:
        rprint("[red]✗ Authentication failed. Please login again.[/red]")
        client.clear_tokens()
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def update():
    """Update user profile"""
    client = get_client()
    
    if not client.is_authenticated():
        rprint("[yellow]Not logged in[/yellow]")
        return
    
    try:
        # Get current user
        user = client.get_current_user()
        
        rprint("[bold]Update Profile[/bold]")
        rprint("[dim]Press Enter to keep current value[/dim]\n")
        
        # Prompt for updates
        email = Prompt.ask(f"Email [{user.email}]", default=user.email)
        username = Prompt.ask(f"Username [{user.username}]", default=user.username)
        full_name = Prompt.ask(
            f"Full Name [{user.full_name or 'Not set'}]", 
            default=user.full_name or ""
        )
        
        # Build update request
        update_data = UpdateUserRequest()
        if email != user.email:
            update_data.email = email
        if username != user.username:
            update_data.username = username
        if full_name != (user.full_name or ""):
            update_data.full_name = full_name if full_name else None
        
        if not update_data.to_dict():
            rprint("[yellow]No changes made[/yellow]")
            return
        
        # Confirm changes
        rprint("\n[bold]Changes to be made:[/bold]")
        for field, value in update_data.to_dict().items():
            rprint(f"  {field}: {value}")
        
        if not Confirm.ask("\nApply these changes?"):
            rprint("[yellow]Update cancelled[/yellow]")
            return
        
        # Apply updates
        with console.status("Updating profile..."):
            updated_user = client.update_current_user(update_data)
        
        rprint("[green]✓ Profile updated successfully![/green]")
        
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--old", prompt="Current password", hide_input=True)
@click.option("--new", prompt="New password", hide_input=True, confirmation_prompt=True)
def change_password(old: str, new: str):
    """Change account password"""
    client = get_client()
    
    if not client.is_authenticated():
        rprint("[yellow]Not logged in[/yellow]")
        return
    
    try:
        with console.status("Changing password..."):
            client.change_password(ChangePasswordRequest(
                old_password=old,
                new_password=new
            ))
        
        rprint("[green]✓ Password changed successfully![/green]")
        rprint("[dim]You can continue using your current session[/dim]")
        
    except AuthenticationError as e:
        if "password" in e.message.lower():
            rprint("[red]✗ Current password is incorrect[/red]")
        else:
            rprint(f"[red]✗ {e.message}[/red]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def health():
    """Check API health status"""
    client = get_client()
    
    try:
        with console.status("Checking API health..."):
            health_data = client.health_check()
        
        # Create health status table
        table = Table(title="API Health Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status")
        
        # API Status
        status_color = "green" if health_data.status == "healthy" else "red"
        table.add_row("API", f"[{status_color}]{health_data.status}[/{status_color}]")
        
        # Database Status
        db_color = "green" if health_data.database == "connected" else "red"
        table.add_row("Database", f"[{db_color}]{health_data.database}[/{db_color}]")
        
        # Version
        table.add_row("Version", health_data.version)
        
        # API URL
        table.add_row("API URL", API_URL)
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[red]✗ Health check failed: {str(e)}[/red]")
        rprint(f"[dim]API URL: {API_URL}[/dim]")
        sys.exit(1)


@cli.command()
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def delete_account(force: bool):
    """Delete your account (irreversible!)"""
    client = get_client()
    
    if not client.is_authenticated():
        rprint("[yellow]Not logged in[/yellow]")
        return
    
    try:
        # Get user info
        user = client.get_current_user()
        
        rprint(f"[red][bold]⚠️  WARNING: Account Deletion[/bold][/red]")
        rprint(f"You are about to delete the account: [bold]{user.username}[/bold]")
        rprint("[red]This action cannot be undone![/red]\n")
        
        if not force:
            # First confirmation
            if not Confirm.ask("Are you sure you want to delete your account?", default=False):
                rprint("[green]Account deletion cancelled[/green]")
                return
            
            # Second confirmation
            confirm_username = Prompt.ask(
                f'Type your username "{user.username}" to confirm'
            )
            if confirm_username != user.username:
                rprint("[red]Username does not match. Cancelling.[/red]")
                return
        
        # Get password
        password = Prompt.ask("Enter your password", password=True)
        
        # Final confirmation
        if not force and not Confirm.ask(
            "[red]This is your last chance. Delete account?[/red]", 
            default=False
        ):
            rprint("[green]Account deletion cancelled[/green]")
            return
        
        # Delete account
        with console.status("Deleting account..."):
            result = client.delete_account(password)
        
        rprint("[green]✓ Account deleted successfully[/green]")
        rprint(result.get("message", "Your account has been deleted"))
        
    except AuthenticationError:
        rprint("[red]✗ Invalid password[/red]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def interactive():
    """Interactive mode with menu"""
    while True:
        console.clear()
        rprint("[bold]FullStack API CLI - Interactive Mode[/bold]\n")
        
        client = get_client()
        if client.is_authenticated():
            try:
                user = client.get_current_user()
                rprint(f"[green]Logged in as: {user.username}[/green]\n")
            except:
                client.clear_tokens()
                rprint("[yellow]Not logged in[/yellow]\n")
        else:
            rprint("[yellow]Not logged in[/yellow]\n")
        
        # Menu options
        options = [
            "1. Login",
            "2. Register",
            "3. Show Profile",
            "4. Update Profile",
            "5. Change Password",
            "6. Check API Health",
            "7. Logout",
            "8. Delete Account",
            "0. Exit"
        ]
        
        for option in options:
            rprint(option)
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
        
        console.clear()
        
        try:
            if choice == "0":
                rprint("[yellow]Goodbye![/yellow]")
                break
            elif choice == "1":
                login()
            elif choice == "2":
                register()
            elif choice == "3":
                whoami()
            elif choice == "4":
                update()
            elif choice == "5":
                ctx = click.Context(change_password)
                change_password.invoke(ctx)
            elif choice == "6":
                health()
            elif choice == "7":
                logout()
            elif choice == "8":
                delete_account(force=False)
        except SystemExit:
            pass  # Catch sys.exit() calls from commands
        
        rprint("\n[dim]Press Enter to continue...[/dim]")
        input()


if __name__ == "__main__":
    cli()