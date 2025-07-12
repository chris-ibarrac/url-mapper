import { Module } from '@nestjs/common';
import { WebhookController } from './app.controller';
import { AppService } from './app.service';
import { HttpModule } from '@nestjs/axios';

@Module({
  imports: [HttpModule],
  controllers: [WebhookController],
  providers: [AppService],
})
export class AppModule {}
