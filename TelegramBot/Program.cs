using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Telegram.Bots;
using Telegram.Bots.Extensions.Polling;

HostApplicationBuilder builder = Host.CreateApplicationBuilder(args);

builder.Configuration.AddUserSecrets<Program>();
string token = builder.Configuration["Token"];
builder.Services.AddBotClient(token);
builder.Services.AddPolling<UpdateHandler>();
var provider = builder.Services.BuildServiceProvider();


IHost host = builder.Build();
host.Run();