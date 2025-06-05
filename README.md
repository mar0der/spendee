# Spendee

This is a Python API wrapper for interfacing with a wonderful [Spendee app](https://www.spendee.com/).

# Warning

No guarantees are provided here. If you wanna use it, go for it, but do know that the original API is undocumented and while it works at the time of writing, it might stop at any time. I'm not associated with Spendee in any way.

# Installation

1. Be Python 3.7+ ready
2. `pip install spendee`
3. Enjoy.

## Future Improvements

- finish up all the endpoints [24/73]
- make dates from the response datetime objects
- release on pypi

## Endpoints

This is a list of all endpoints I've discovered. So far only a subset is implemented:

- [ ] v1/exchange-rate
- [ ] v1/notification-count-unread
- [ ] v1/notification-get-all
- [ ] v1/notification-set
- [ ] v1/user-check-email
- [ ] v1/user-set-subscription
- [ ] v1/wallet-accept-sharing
- [ ] v1/wallet-get
- [ ] v1/wallet-get-category
- [ ] v1/wallet-get-users
- [ ] v1/wallet-order-categories
- [ ] v1.3/currencies
- [ ] v1.3/delete-bank-login
- [ ] v1.4/confirm-deletion
- [ ] v1.4/confirm-email-change
- [ ] v1.4/merge-categories
- [ ] v1.4/recommendation-likelihood
- [ ] v1.4/request-deletion
- [ ] v1.4/request-email-change
- [ ] v1.4/user-forgot-password
- [ ] v1.4/user-get-profiles
- [ ] v1.4/user-password-change-confirmation
- [ ] v1.4/wallet-get-categories
- [ ] v1.5/change-to-two-way-transfer
- [ ] v1.5/delete-transfer-transaction
- [ ] v1.5/link-two-transactions-into-transfer
- [ ] v1.5/revert-transfer-to-regular-transaction
- [ ] v1.5/transaction-suggestions
- [ ] v1.5/transfer-funds
- [ ] v1.5/update-transfer
- [ ] v1.5/user-fb-connect
- [ ] v1.5/user-google-connect
- [ ] v1.5/viewed-dialogs
- [ ] v1.5/wallet-create-transaction
- [ ] v1.5/wallet-delete-transaction
- [ ] v1.5/wallet-update-transaction
- [ ] v1.6/get-transactions
- [ ] v1.6/iframe-wallet-data?id=
- [ ] v1.6/reorder-wallets
- [ ] v1.6/wallet-get-transaction
- [ ] v1.7/reorder-budgets
- [ ] v1.8/create-transaction-template
- [ ] v1.8/delete-transaction-template
- [ ] v2/destroyCredentials
- [X] v1.3/banks-get-all
- [X] v1.3/category-image-ids
- [X] v1.4/user-get-profile
- [X] v1.4/user-login
- [X] v1.4/user-logout
- [X] v1.4/wallet-create-category
- [X] v1.4/wallet-update-category
- [X] v1.5/user-registration
- [X] v1.5/user-update-profile
- [X] v1.6/get-all-user-categories
- [X] v1.6/user-currencies
- [X] v1.7/create-budget
- [X] v1.7/delete-budget
- [X] v1.7/edit-budget
- [X] v1.7/get-budgets
- [X] v1.8/get-transaction-templates
- [X] v1.8/wallet-get-transactions
- [X] v1/wallet-create
- [X] v1/wallet-delete
- [X] v1/wallet-delete-category
- [X] v1/wallet-get-all
- [X] v1/wallet-invite-to-share
- [X] v1/wallet-unshare-user
- [X] v1/wallet-update
- [X] v2/countries
- [X] v2/logins/refresh
- [X] v2/providers
- [X] v2/url
- [X] v2/visible

## Contributing

If you can improve anything in this repo, feel free to add a pull request or add an issue!

## PHP 8.2 Docker Environment Example

The `php_docker_env` directory contains a simple development setup with PHP 8.2, nginx and MySQL running in two Docker containers. To try it out you will need [Docker](https://www.docker.com/) with the Compose plugin installed.

1. Open a terminal and change into the example directory:

   ```bash
   cd php_docker_env
   ```

2. Build the web container and start the stack:

   ```bash
   docker compose up --build
   ```

   The first run downloads the base images and may take a minute.

3. Visit [http://localhost:8080](http://localhost:8080) in your browser. A `phpinfo()` page should appear confirming that PHP is running through nginx.

The MySQL server listens on port `3306` with credentials defined in `docker-compose.yml`. When you are done, stop the environment with `docker compose down`.

