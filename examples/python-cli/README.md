# FullStack Python CLI Example

A feature-rich command-line interface for the FullStack API, demonstrating Python SDK usage.

## Features

- 🔐 Secure authentication with token persistence
- 👤 User registration and profile management
- 🔑 Password management
- 🏥 API health monitoring
- 🎨 Rich terminal UI with colors and tables
- 📝 Interactive and command modes
- ⚡ Automatic token refresh
- 🛡️ Comprehensive error handling

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install the Python SDK (from root directory):
```bash
cd ../../sdk/python
pip install -e .
```

3. Configure environment (optional):
```bash
# Create .env file
echo "FULLSTACK_API_URL=http://localhost:8000" > .env
```

## Usage

### Command Mode

Run individual commands:

```bash
# Show help
./fullstack_cli.py --help

# Login
./fullstack_cli.py login

# Register new account
./fullstack_cli.py register

# Show current user
./fullstack_cli.py whoami

# Update profile
./fullstack_cli.py update

# Change password
./fullstack_cli.py change-password

# Check API health
./fullstack_cli.py health

# Logout
./fullstack_cli.py logout

# Delete account
./fullstack_cli.py delete-account
```

### Interactive Mode

Launch interactive menu:

```bash
./fullstack_cli.py interactive
```

## Commands

### `login`
Authenticate with username and password. Tokens are stored in `~/.fullstack/cli_tokens.json`.

```bash
$ ./fullstack_cli.py login
Username: john_doe
Password: ********
✓ Successfully logged in as john_doe!
```

### `register`
Create a new account with optional auto-login.

```bash
$ ./fullstack_cli.py register
Register New Account
Email: john@example.com
Username: john_doe
Full Name (optional): John Doe
Password: ********
Confirm Password: ********
✓ Account created successfully!
Do you want to login now? [Y/n]: y
✓ Logged in as john_doe
```

### `whoami`
Display detailed information about the current user.

```bash
$ ./fullstack_cli.py whoami
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      User Information              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ID       │ 123e4567-e89b-12d3...  │
│ Username │ john_doe                │
│ Email    │ john@example.com        │
│ Full Name│ John Doe                │
│ Active   │ Yes                     │
│ Verified │ Yes                     │
│ Superuser│ No                      │
│ Created  │ 2024-01-15 10:30:00     │
│ Updated  │ 2024-01-15 10:30:00     │
└────────────────────────────────────┘
```

### `update`
Update user profile information interactively.

```bash
$ ./fullstack_cli.py update
Update Profile
Press Enter to keep current value

Email [john@example.com]:
Username [john_doe]:
Full Name [John Doe]: John Smith

Changes to be made:
  full_name: John Smith

Apply these changes? [y/N]: y
✓ Profile updated successfully!
```

### `change-password`
Change account password with validation.

```bash
$ ./fullstack_cli.py change-password
Current password: ********
New password: ********
Repeat for confirmation: ********
✓ Password changed successfully!
```

### `health`
Check API and database status.

```bash
$ ./fullstack_cli.py health
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    API Health Status       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ API      │ healthy        │
│ Database │ connected      │
│ Version  │ 1.0.0          │
│ API URL  │ http://loc...  │
└────────────────────────────┘
```

### `logout`
Logout and clear stored tokens.

```bash
$ ./fullstack_cli.py logout
✓ Successfully logged out
```

### `delete-account`
Permanently delete account with multiple confirmations.

```bash
$ ./fullstack_cli.py delete-account
⚠️  WARNING: Account Deletion
You are about to delete the account: john_doe
This action cannot be undone!

Are you sure you want to delete your account? [y/N]: y
Type your username "john_doe" to confirm: john_doe
Enter your password: ********
This is your last chance. Delete account? [y/N]: y
✓ Account deleted successfully
```

## Features Demonstrated

### Token Persistence
Tokens are stored securely in `~/.fullstack/cli_tokens.json` with restricted permissions (600).

### Rich Terminal UI
Uses the `rich` library for:
- Colored output
- Progress indicators
- Formatted tables
- Interactive prompts

### Error Handling
Comprehensive error handling for:
- Authentication failures
- Validation errors
- Rate limiting
- Network issues

### Interactive Mode
Full menu-driven interface for users who prefer not to use individual commands.

## Development

### Project Structure
```
python-cli/
├── fullstack_cli.py    # Main CLI application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env              # Environment configuration (optional)
```

### Adding New Commands

To add a new command:

```python
@cli.command()
@click.option("--example", help="Example option")
def new_command(example: str):
    """Description of your command"""
    client = get_client()

    # Your command logic here
    pass
```

### Error Handling Pattern

```python
try:
    # API call
    result = client.some_method()
except AuthenticationError as e:
    rprint(f"[red]✗ Auth failed: {e.message}[/red]")
    sys.exit(1)
except ValidationError as e:
    rprint("[red]✗ Validation errors:[/red]")
    for error in e.errors:
        rprint(f"  - {error['field']}: {error['message']}")
    sys.exit(1)
except Exception as e:
    rprint(f"[red]✗ Error: {str(e)}[/red]")
    sys.exit(1)
```

## Security Notes

1. Tokens are stored in user's home directory with restricted permissions
2. Passwords are never stored, only masked input
3. Multiple confirmations for destructive actions
4. Automatic token cleanup on errors

## Troubleshooting

### "Not logged in" error
Run `./fullstack_cli.py login` to authenticate.

### Token expired
The CLI will attempt to refresh automatically. If that fails, login again.

### Connection errors
Check the API URL in your `.env` file or environment variables.

### Permission denied
Make the script executable: `chmod +x fullstack_cli.py`
