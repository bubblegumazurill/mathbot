''' Module to allow the user to roll dice '''

import re
import random

import core.module
import core.handles
import core.help
import core.settings
import math

core.help.load_from_file('./help/roll.md')

FORMAT_REGEX = re.compile(r'^(?:(\d*)[ d]+)?(\d+)$')


class TooManyFacesException(Exception): pass


class TooManyDiceException(Exception): pass


class DiceModule(core.module.Module):

	''' Module to allow the user to roll dice '''

	@core.handles.command('roll', '*', perm_setting='c-roll')
	async def command_roll(self, message, arg):
		''' Roll command. Argument should be of the format `2d6` or similar. '''
		match = FORMAT_REGEX.match(arg.strip('`'))
		if match is None or match.group(2) is None:
			return '🎲 Format your rolls like `2d6`.'
		dice, faces = match.group(1, 2)
		dice = int(dice or 1)
		faces = int(faces or 6)
		if faces <= 0:
			return '🎲 Dice must have a positive number of faces.'

		limit = await self.get_limit(message)		

		# this is the minimal length of this query
		min_len = 2 * dice + 9 + math.log10(dice)

		if min_len >= limit:
			total = 0
			try:
				total = self.gaussian_roll(dice, faces)
			except TooManyDiceException:
				return '🎲 You have tried to roll too many dice.'
			except TooManyFacesException:
				return '🎲 You have tried to roll too many faces.'

			return f'🎲 total: {total}'
		else:
			rolls, total = self.formatted_roll(dice, faces)
			final_message = f'🎲 {rolls}'
			return final_message if len(final_message) <= limit else f'🎲 total: {total}'

	async def get_limit(self, message):
		unlimited = await core.settings.resolve_message('f-roll-unlimited', message)
		print(unlimited)
		return 100 if not unlimited else 2000

	def formatted_roll(self, dice, faces):
		rolls = [random.randint(1, faces) for _ in range(dice)]
		s = f'{str.join(" ", (str(i) for i in rolls))} (total: {sum(rolls)})'
		return s, sum(rolls)

	def gaussian_roll(self, dice, faces):
		if math.log10(dice) < 16 and\
			math.log10(faces) < 16 and\
			math.log10(dice * faces) < 16:
			return self.gaussian_roll_single(dice, faces)
		elif math.log10(faces) < 16:
			dice_per = 16 - round(math.log10(faces))
			times = round(dice / 10**(dice_per))
			if times > 100000:
				raise TooManyDiceException()
			return sum([self.gaussian_roll_single(dice_per, faces) for _ in range(times)])
		else:
			raise TooManyFacesException()

	def gaussian_roll_single(self, dice, faces):
		mean = (faces + 1) * dice / 2
		std = math.sqrt((dice * (faces * faces - 1)) / 12)
		return int(random.gauss(mean, std))
