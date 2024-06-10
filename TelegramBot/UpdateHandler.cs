using Telegram.Bots;
using Telegram.Bots.Extensions.Polling;
using Telegram.Bots.Requests;
using Telegram.Bots.Types;
 
internal class UpdateHandler : IUpdateHandler
{
    public async Task HandleAsync(IBotClient bot, Update update, CancellationToken token)
    {
        if (update is MessageUpdate u)
        {
            SendText request = new( u.Data.Chat.Id,  "Hello!");

            Response<TextMessage> response = await bot.HandleAsync(request);

            if (response.Ok)
            {
                TextMessage message = response.Result;

                Console.WriteLine(message.Id);
                Console.WriteLine(message.Text);
                Console.WriteLine(message.Date.ToString("G"));
            }
            else
            {
                Failure failure = response.Failure;

                Console.WriteLine(failure.Description);
            }
        }
    }
}