import { Controller, Post, Get, Body, Query } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import * as fs from 'fs/promises';
import { join } from 'path';

@Controller()
export class WebhookController {
  constructor(private readonly http: HttpService) {}

  @Get()
  getPing(): string {
    return 'OK';
  }

  @Post("/app")
  async urlMapper(@Body() event: any, @Query('id') id: number) {
   if (event.challenge) {
      return event;
    } 
    const parsedData =  await this.readJson('apps.json');
    return parsedData.apps.find((app) => app.id === Number(id)) ?? { error: 'App not found for given ID' };
  }

  @Post()
  async handleWebhook(@Body() event: any) {
    if (event.challenge) {
      return event;
    }
    try {
      const { data } = await firstValueFrom(
        this.http.get<{ url: string }>('https://webhooks-monday-default-rtdb.firebaseio.com/api/ngrok.json')
      );
      if (!data.url) {
        return { error: 'Ngrok URL not found' };
      }
      const response = await firstValueFrom(
        this.http.post(data.url, event, {
          headers: { 'Content-Type': 'application/json' },
        })
      );
      return response.data;
    } catch (error) {
      console.error('Webhook error:', error);
      return { error: 'Failed to process webhook' };
    }
  }

  private async readJson(filePath: string) {
    return JSON.parse(
      await fs.readFile( join(__dirname, '..', '.', filePath), 'utf-8'))
  }
}